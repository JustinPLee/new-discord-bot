import discord
import sqlite3
from typing import Union

from bot.user import User

from db.database import Database
from log import log

# basically stores all data
# controller for db operations
class Manager:
    def __init__(self, apis: dict, embeds: dict):
        self._apis = apis
        self._embeds = embeds

        self.dbfile = "db/users.sqlite"

        self.create_tables()

    def embed(self, name: str, **kwargs: any) -> discord.Embed:
        """
        Wrapper for creating an embed. Arguments must exactly match the embed's `generate` function.

        Parameters
        ----------
        name: `str`
            Name of an embed set at a Manager object's initialization.
        **kwargs: `any`
            The specified embed's required arguments
        """

        return self._embeds[name].generate(**kwargs)

    def api_call(self, name: str, **kwargs) -> str:
        """
        Wrapper for calling an api. Arguments must exactly match the api's `extract` function.

        Parameters
        ----------
        name: `str`
            Name of an api set at a Manager object's initialization.
        **kwargs: `any`
            The specified api's required arguments
        """

        return self._apis[name].extract(**kwargs)

    def location_exists(self, name: str, location: str) -> bool:
        """
        Calls the api's `location_exists` function with the provided arguments.

        Parameters
        ----------
        name: `str`
            Name of an api set at a Manager object's initialization.
        """

        return self._apis[name].location_exists(location)

    def get_user(self, user_id: int) -> User:
        """
        Returns a `User` object with data from the database.

        Parameters
        ----------
        user_id: `int`
            18 digit Discord user id.
        """

        get_user_with_id = """
            SELECT
                *
            FROM
                users
            WHERE
                id = ?
        """
        tuppy = ()
        try:
            with Database(self.dbfile) as db:
                db.execute(get_user_with_id, (user_id,))
                tuppy = db.fetchone()
        except sqlite3.Error as err:
            log(err + f" - in get_user(user_id={user_id})")

        return Manager.convert_tuple_to_user(tuppy)

    def update_location(self, user_id: int, new_location: str) -> None:
        """
        Updates the location of a user.

        Parameters
        ----------
        user_id: `int`
            18 digit Discord user id.
        new_location: `str`
        """

        update_users_location = """
            UPDATE
                users
            SET
                location = ?
            WHERE id = ?
        """
        try:
            with Database(self.dbfile) as db:
                db.execute(update_users_location, (new_location, user_id))
                db.commit()
        except sqlite3.Error as err:
            log(err + f" - in update_location(user_id={user_id}, new_location={new_location})")

    def update_signup(self, user_id: int, is_signed_up: bool) -> None:
        """
        Updates the `is_signed_up` attribute of a user.

        Parameters
        ----------
        user_id: `int`
            18 digit Discord user id.
        is_signed_up: `bool`
        """

        update_user_signup = """
            UPDATE
                users
            SET
                is_signed_up = ?
            WHERE id = ?
        """
        try:
            with Database(self.dbfile) as db:
                db.execute(update_user_signup, (+(is_signed_up), user_id))
                db.commit()
        except sqlite3.Error as err:
            log(err + f" - in update_signup(user_id={user_id}, is_signed_up={is_signed_up})")

    def add_user(self, user: User) -> None:
        """
        Adds a `User` to the database. Do not add the same user more than once.

        Parameters
        ----------
        user: `User`
        """

        populate_table = """
            INSERT INTO users
                (
                    id,
                    display_name,
                    display_avatar,
                    location,
                    is_signed_up
                ) VALUES(?, ?, ?, ?, ?)
        """
        try:
            with Database(self.dbfile) as db:
                db.execute(populate_table, (user.id, user.display_name, user.display_avatar, user.location, +(user.is_signed_up)))
                db.commit()
        except sqlite3.Error as err:
            log(err + f" - in add_user(user={User})")

    def exists_user(self, user_id: int) -> bool:
        """
        Returns whether a user is in the database.

        Parameters
        ----------
        user_id: `int`
            18 digit Discord user id.
        """

        get_user = """
            SELECT
                1
            FROM
                users
            WHERE id = ?
        """
        try:
            with Database(self.dbfile) as db:
                db.execute(get_user, (user_id,))
                return db.fetchone() is not None
        except sqlite3.Error as err:
            log(err + f" - in exists_user(user_id={user_id})")

    def get_signed_up(self) -> list[User]:
        """
        Returns a list of `User` objects whose `is_signed_up` attribute is true.

        Parameters
        ----------
        None
        """
        find_signed_up = """
            SELECT
                id
            FROM
                users
            WHERE
                is_signed_up = 1
        """
        tuppies = []
        try:
            with Database(self.dbfile) as db:
                db.execute(find_signed_up)
                tuppies = db.fetchall()
        except sqlite3.Error as err:
            log(err + f"- in get_signed_up")

        return [id[0] for id in tuppies]

    def add_reminder(self, user_id: int, reminder: str) -> None:
        """
        Adds a user's reminder to the database. Reminders are automatically indexed.

        Parameters
        ----------
        user_id: `int`
            18 digit Discord user id .
        reminder: `str`
        """

        if reminder == "":
            return None

        get_cur_r_index = """
            SELECT
                COUNT(reminder)
            FROM
                reminders
            WHERE
                owner_id = ?
        """
        add_reminder = """
            INSERT INTO reminders
                (owner_id, r_index, reminder)
                VALUES(?, ?, ?)
        """
        try:
            with Database(self.dbfile) as db:
                db.execute(get_cur_r_index, (user_id,))
                r_index = db.fetchone()[0]
                db.execute(add_reminder, (user_id, r_index, reminder))
                db.commit()
        except sqlite3.Error as err:
            log(err + f" - in add_reminder(user_id={user_id}, reminder={reminder})")

    def remove_reminder(self, user_id: int, index: int) -> None:
        """
        Removes a user's reminder at index: `index`.

        Parameters
        ----------
        user_id: `int`
            18 digit Discord user id.
        index: `int`
            Raises if index is not valid.
        """

        if index < 0:
            raise IndexError
        
        try:
            with Database(self.dbfile) as db:
                max = len(self.get_reminders(user_id))
                if index >= max:
                    raise IndexError
        
                delete_reminder = """
                    DELETE FROM
                        reminders
                    WHERE
                        owner_id = ?
                    AND
                        r_index = ?
                """
                try:
                    db.execute(delete_reminder, (user_id, index))
                except sqlite3.Error as err:
                    log(err + f" - in delete_reminder in remove_reminder(user_id={user_id}, index={index})")
                # subtract one to the indexes of reminders higher than the index removed 
                # simulates removal from an array
                while index < max:
                    reorder_indexes = """
                        UPDATE
                            reminders
                        SET
                            r_index = ?
                        WHERE
                            owner_id = ?
                        AND
                            r_index = ?
                    """
                    try:
                        db.execute(reorder_indexes, (index, user_id, index+1))
                    except sqlite3.Error as err:
                        log(err + f" - in reorder_indexes(index={index}, user_id={user_id}, index={index+1} in remove_reminders(user_id={user_id}, index={index}))")
                    index += 1
                db.commit()
        except sqlite3.Error as err:
            log(err + f" - in remove_reminder(user_id={user_id}, index={index})")

    def get_reminders(self, user_id: int) -> list[str]:
        """
        Returns a list of a user's reminders.

        Parameters
        ----------
        user_id: `int`
            18 digit Discord user id.
        """

        get_user_reminders = """
            SELECT
                reminder
            FROM
                reminders
            WHERE
                owner_id = ?
            ORDER BY
                r_index ASC
        """
        tuppy = ()
        try:
            with Database(self.dbfile) as db:
                db.execute(get_user_reminders, (user_id,))
                tuppy = db.fetchall()
        except sqlite3.Error as err:
            log(err + f" - in get_reminders(user_id={user_id})")        
        if tuppy is None:
            return []
        else:
            return [reminder[0] for reminder in tuppy]

    def create_tables(self) -> None:
        try:
            with Database(self.dbfile) as db:
                try:
                    self.create_users_table(db)
                except sqlite3.Error as err:
                    log(err + f" - in create_users_table")
                try:
                    self.create_reminders_table(db)
                except sqlite3.Error as err:
                    log(err + f" - in create_reminders_table")
                db.commit()
        except sqlite3.Error as err:
            log(err + f" - in create_tables")

    def create_reminders_table(self, db: Database) -> None:
        reminders_table = """
            CREATE TABLE IF NOT EXISTS
                reminders (
                    owner_id INTEGER,
                    r_index INTEGER NOT NULL,
                    reminder TEXT NOT NULL,
                    FOREIGN KEY (owner_id) REFERENCES users (id)
                );
        """
        db.execute(reminders_table)

    def create_users_table(self, db: Database) -> None:
        users_table = """
            CREATE TABLE IF NOT EXISTS
                users (
                    id INTEGER PRIMARY KEY,
                    display_name TEXT NOT NULL,
                    display_avatar TEXT NOT NULL,
                    location TEXT NOT NULL,
                    is_signed_up BIT default 0
                );
        """
        db.execute(users_table)

    @staticmethod
    def convert_tuple_to_user(welovetuples: Union[tuple, list[tuple]]) -> Union[User, list[User]]:
        """
        Converts a tuple or list or tuples to a `User` object.
        Returns a single `User` or a list of `User`s.

        Parameters
        ----------
        welovetuples: `tuple`|`list[tuple]`
            Tuple of `User` attributes.
        """
        assert tuple != () and tuple is not None
        assert isinstance(welovetuples, tuple) or isinstance(welovetuples, list)

        if isinstance(welovetuples, tuple):
            id, dn, da, l, isu = welovetuples
            return User(id=id, display_name=dn, display_avatar=da, location=l, is_signed_up=isu)
        elif isinstance(welovetuples, list):
            users = []
            for tuppy in welovetuples:
                id, dn, da, l, isu = tuppy
                users += [User(id=id, display_name=dn, display_avatar=da, location=l, is_signed_up=isu)]

            return users