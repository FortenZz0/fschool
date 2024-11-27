from netschoolapi import NetSchoolAPI

from handlers import database


db = database.DB()


trans_table = {
    ord("\n"): " ",
    ord("\t"): " ",
    ord("\b"): " "
}


# --- SELF METHODS ---

# Добавляет / в конце ссылки при необходимости
format_url = lambda x: x if x[-1] == "/" else x + "/"


def new_user(tg_username: str,
             url: str,
             login: str,
             password: str,
             school: str):
    """Записывает нового юзера в базу данных

    Args:
        tg_username (str): Тг юз пользователя
        url (str): Ссылка на электронный журнал
        login (str): Логин юзера
        password (str): Пароль юзера
        school (str): Название школы
    """
    
    db.execute(
        "INSERT INTO users(username, url, login, password, school, cycle) VALUES(?, ?, ?, ?, ?, 'quarters')",
        (tg_username,
         url,
         login,
         password,
         school)
    )
    
    db.commit()


def get_user(username: str) -> tuple:
    """Возвращает запись юзера из базы данных

    Args:
        username (str): Тг юзернейм (@*)

    Returns:
        tuple: Запись юзера в бд
    """
    
    db.execute("SELECT * FROM users WHERE username = ?", (username,))
    return db.fetchone()
    
    
def get_admin(username: str) -> tuple:
    """Возвращает запись админа из базы данных

    Args:
        username (str): Тг юзернейм (@*)

    Returns:
        tuple: Запись админа в бд
    """
    
    db.execute("SELECT * FROM admins WHERE username = ?", (username,))
    return db.fetchone()
    

async def ns_login(url: str | None = None,
             login: str | None = None,
             password: str | None = None,
             school: str | None = None,
             tg_username: str | None = None) -> NetSchoolAPI | None:
    """Выполняет вход в электронный журнал. Если указан tg_username, то вход будет произведён с использованием базы данных

    Args:
        url (str | None, optional): Ссылка на электронный журнал. Defaults to None
        login (str | None, optional): Логин юзера. Defaults to None
        password (str | None, optional): Пароль юзера. Defaults to None
        school (str | None, optional): Название школы. Defaults to None
        tg_username (str | None, optional): Тг юз пользователя. Defaults to None

    Returns:
        NetSchoolAPI: Объект NetSchoolAPI
    """
    
    data = [url, login, password, school]
    
    if tg_username:
        admin = get_admin(tg_username)
        
        if admin:
            tg_username = admin[1]
        
        data = get_user(tg_username)[1:-1]
        
    ns = NetSchoolAPI(data[0])
    
    if ns:
        try:
            await ns.login(*data[1:])
            
            return ns
        except:
            return None
    else:
        return None
    
    

