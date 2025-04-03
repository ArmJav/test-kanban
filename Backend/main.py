from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from database import SessionLocal, Role,User,BaseZ, TaskModel, OrderModel
from jose import JWTError, jwt
from models import UserRegistration,NewRole,TaskSchema, TaskGetSchema, SetPrioritySchema, TaskEditSchema, IdSchema
from datetime import datetime, timedelta
from typing import Optional,Annotated
from bcrypt import checkpw,hashpw,gensalt
from config import DATABASE_URL, SECRET_KEY,ALGORITHM,ACCESS_TOKEN_EXPIRE_MINUTES,ADMIN_ROLE
from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from itertools import zip_longest

'''
КОД ПО РАБОТЕ С ПОЛЬЗОВАТЕЛЯМИ
'''
app = FastAPI(title='API По работе с задачами',version='0.1.0')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate dsds",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id : int = payload.get('id')
        username: str = payload.get("sub")
        if username is None or id is None:
            raise credentials_exception
    
    except JWTError:
        raise credentials_exception
    return username,id

@app.post("/token",
          summary='Авторизация токена', 
          tags=['Авторизация'])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    db: Session = SessionLocal()
    user = db.query(User).filter(User.username == form_data.username).first()    
    if not user or not checkpw(form_data.password.encode('utf-8'), user.hashed_password.encode('utf-8')):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={'id':user.id,"sub": user.username})
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/register", 
          summary='Регистрация',
          tags=['Авторизация'])
async def register(reg_model:UserRegistration):
    db: Session = SessionLocal()
    hashed_password = hashpw(reg_model.password.encode('utf-8'),gensalt()).decode('utf-8')
    date = datetime.now()
    new_user = User(username=reg_model.username, hashed_password=hashed_password, name = reg_model.name,surname=reg_model.surname,pathynomic=reg_model.pathynomic,description = reg_model.description,date_of_registration=date,role_id = 2)
    db.add(new_user)
    db.commit()
    access_token = create_access_token(data={'id':new_user.id,"sub": new_user.username})
    return {"access_token": access_token, "token_type": "bearer",'msg"': 'Регистрация прошла успешно'}

@app.post('/createrole', 
          summary='Создание новой роли',
          tags=['Работа с юзерами'])
async def create_new_role(role:NewRole,user_role: str = Depends(get_current_user)):
    db : Session = SessionLocal()
    user = db.query(User).filter(User.id == user_role[1]).first()
    if user and user.role_id == ADMIN_ROLE:
        new_role = Role(role_name = role.role_name) 
        db.add(new_role)
        db.commit()
        return {'status':'ok'}
    else:
        raise HTTPException(status_code=403, detail="Not Found")
    
@app.post('/delete_role', 
          summary='Удаление роли',
          tags=['Работа с юзерами'])
async def delete_role(role_id:int ,user_role: str = Depends(get_current_user)):
    db : Session = SessionLocal()
    user = db.query(User).filter(User.id == user_role[1]).first()
    if user and user.role_id == ADMIN_ROLE:
        this_role = db.query(Role).filter(Role.id == role_id).first()
        if not this_role:
            raise HTTPException(status_code=404, detail="Not Found")
        else:
            db.delete(this_role)
            db.commit()
        return {'status':'ok'}
    else:
        raise HTTPException(status_code=403, detail="Not Found")

@app.post("/deleteuser", 
          summary='Удаление пользователя',
          tags=['Работа с юзерами'])
async def delete_user(user_id: int,user_role: str = Depends(get_current_user)):
    db: Session = SessionLocal()
    user = db.query(User).filter(User.id == user_role[1]).first()
    if user and user.role_id == ADMIN_ROLE:
        this_user = db.query(User).filter(User.id == user_id).first()
        if user_id == user.role_id:
            return {'msg': 'Ты пытаешься удалить себя'} 
        if not this_user:
            raise HTTPException(status_code=404, detail="Not Found")
        else:
            db.delete(this_user)
            db.commit()
            return {'msg"': 'Юзер успешно удален'}
    else:
        raise HTTPException(status_code=403, detail="Not Found")

@app.get("/users/me/", 
         summary='Информация о вошедшем юзере',
         tags=['Авторизация'])
async def read_users_me(current_user: str = Depends(get_current_user)):
    db: Session = SessionLocal()
    user = db.query(User).filter(User.id == current_user[1]).first()
    get_user_role = db.query(Role).filter(Role.id==user.role_id).first()
    if not user:
        raise HTTPException(status_code=403, detail="User not found")
    return {"name": user.name,'surname':user.surname,'pathynomic':user.pathynomic,'description':user.description,'date_of_registration':user.date_of_registration,'role':get_user_role.role_name}
'''
КОД ПО РАБОТЕ С ТАСКАМИ
'''
engine = create_async_engine("sqlite+aiosqlite:///mydb.db", echo=True)

new_async_session = async_sessionmaker(engine, expire_on_commit=False)

def check_on_admin(current_user):
    db: Session = SessionLocal()
    user = db.query(User).filter(User.id == current_user[1]).first()
    if user and user.role_id == ADMIN_ROLE:
        return user
    else:
        return None

async def get_session():
    async with new_async_session() as session:
        yield session
SessionDep = Annotated[AsyncSession, Depends(get_session)]


@app.post("/add_task", tags=["Изменение задач"], summary='Добавить задачу')
async def add_task(task: TaskSchema, session: SessionDep,current_user = Depends(get_current_user)) -> dict:
    db: Session = SessionLocal()
    user = db.query(User).filter(User.id == current_user[1]).first()
    new_task = TaskModel(
        title=task.title,
        text=task.text,
        executor=f'{user.surname} {user.name} {user.pathynomic}',
        creation_time=datetime.now(),
        priority_not_set=True
    )
    session.add(new_task)

    await session.commit()
    return {"status": "Ok"}


@app.post("/set_priority", tags=["Изменение задач"], summary='Изменить приоритет задачи.'
                                                             ' Поле status принимает одно из трех значений:'
                                                             ' backlog, processing, completed. Если ввести priority=0,'
                                                             ' то приоритет задачи будет удален.')
async def set_priority(schema: SetPrioritySchema, session: SessionDep,current_user = Depends(get_current_user)) -> dict:
    query = select(TaskModel).where(TaskModel.id == schema.task_id)
    result = await session.execute(query)
    tasks = result.scalars().all()

    if not tasks:
        raise HTTPException(status_code=404, detail="There is no task with this id")

    task = tasks[0]

    task.priority_not_set = False
    session.add(task)

    query = select(OrderModel)
    result = await session.execute(query)
    orders = result.scalars().all()

    if not orders:
        orders = [OrderModel(backlog=" ", processing=" ", completed=" ")]

    for i in ["backlog", "processing", "completed"]:
        orders[0][i] = orders[0][i].replace(str(schema.task_id), '')

    if schema.priority == 0:
        query = select(TaskModel).where(TaskModel.id == schema.task_id)
        result = await session.execute(query)
        task = result.scalars().all()[0]
        task.priority_not_set = True
        session.add(task)
        await session.commit()
        return {"status": "Ok"}

    order = orders[0][schema.status].split()
    order = " ".join(order[:schema.priority - 1] + [str(schema.task_id)] + order[schema.priority - 1:])

    orders[0][schema.status] = order
    session.add(orders[0])

    await session.commit()
    return {"status": "Ok"}


@app.get("/get_tasks", tags=["Запрос задач"], summary="Возвращает три списка, отсортированных в зависимости от"
                                                      " установленных приоритетов. Если для задачи не установлен"
                                                      " приоритет, то она не возвращается.")
async def get_tasks(session: SessionDep) -> dict[str, list[TaskGetSchema]]:
    query_tasks = select(TaskModel)
    result = await session.execute(query_tasks)
    tasks = result.scalars().all()

    query_orders = select(OrderModel)
    result = await session.execute(query_orders)
    orders = result.scalars().all()

    backlog, processing, completed = [], [], []

    dict_tasks = dict()
    for t in tasks:
        dict_tasks[t.id] = t

    for i, j, k in zip_longest(orders[0]["backlog"].split(), orders[0]["processing"].split(), orders[0]["completed"].split()):
        if i:
            backlog.append(dict_tasks[int(i)])
        if j:
            processing.append(dict_tasks[int(j)])
        if k:
            completed.append(dict_tasks[int(k)])

    data = {
        'backlog': backlog,
        'processing': processing,
        'completed': completed
    }

    return data

@app.get("/get_tasks_without_priority", tags=["Запрос задач"], summary="Возвращает задачи,"
                                                                          " для которых приоритет не был установлен")
async def get_tasks_without_priority(session: SessionDep,current_user = Depends(get_current_user)) -> list[TaskGetSchema]:
    query_tasks = select(TaskModel).where(TaskModel.priority_not_set)
    result = await session.execute(query_tasks)
    tasks = result.scalars().all()
    return tasks


@app.get("/get_task/{task_id}", tags=["Запрос задач"], summary="Возвращает задачу по id.")
async def get_task(task_id: int, session: SessionDep,current_user = Depends(get_current_user)) -> TaskGetSchema:
    query = select(TaskModel).where(TaskModel.id == task_id)
    result = await session.execute(query)
    tasks = result.scalars().all()
    if tasks:
        return tasks[0]
    raise HTTPException(status_code=404, detail="There is no task with this id")


@app.post("/edit_task", tags=["Изменение задач"], summary='Редактировать задачу.'
                                                          ' Если редактировать какое-то конкретное поле не нужно,'
                                                          ' используйте символ "~". Например: "title": "~".')
async def edit_task(task: TaskEditSchema, session: SessionDep) -> dict:
    query = select(TaskModel).where(TaskModel.id == task.id)
    result = await session.execute(query)
    tasks = result.scalars().all()

    if not tasks:
        raise HTTPException(status_code=404, detail="There is no task with this id")

    edited_task = tasks[0]

    if task.title != "~":
        edited_task.title = task.title
    if task.text != "~":
        edited_task.text = task.text
    if task.executor != "~":
        edited_task.executor = task.executor

    session.add(edited_task)
    await session.commit()
    return {"status": "Ok"}

@app.post("/delete_task", tags=["Изменение задач"], summary="Удалить задачу")
async def delete_task(task: IdSchema, session: SessionDep,current_user = Depends(get_current_user)) -> dict:
    check = check_on_admin(current_user)
    
    if check:
        query = select(TaskModel).where(TaskModel.id == task.id)
        result = await session.execute(query)
        tasks = result.scalars().all()
        
        if not tasks:
            raise HTTPException(status_code=404, detail="There is no task with this id")

        query = delete(TaskModel).where(TaskModel.id == task.id)
        await session.execute(query)

        query_orders = select(OrderModel)
        result = await session.execute(query_orders)
        orders = result.scalars().all()

        for i in ["backlog", "processing", "completed"]:
            orders[0][i] = orders[0][i].replace(str(task.id), '')
        await session.commit()
        
        return {"status": "Ok"}
    
    else:
        raise HTTPException(status_code=403, detail="Not Found")
