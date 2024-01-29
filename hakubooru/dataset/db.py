import pathlib
import sqlite3

from numpy import base_repr
from peewee import *
from playhouse.sqlite_ext import FTS5Model, SearchField
from playhouse.shortcuts import model_to_dict


class MemoryConnection(sqlite3.Connection):
    def __init__(self, dbname, *args, **kwargs):
        load_conn = sqlite3.connect(dbname)
        super(MemoryConnection, self).__init__(":memory:", *args, **kwargs)
        load_conn.backup(self)
        load_conn.close()


class SqliteMemDatabase(SqliteDatabase):
    def __init__(self, database, *args, **kwargs) -> None:
        self.dbname = database
        super().__init__(database, *args, factory=MemoryConnection, **kwargs)

    def reload(self, dbname=None):
        if dbname is None:
            dbname = self.dbname
        load_conn = sqlite3.connect(dbname)
        try:
            load_conn.backup(self._state.conn)
        finally:
            load_conn.close()

    def save(self, dbname=None):
        if dbname is None:
            dbname = self.dbname
        save_conn = sqlite3.connect(dbname)
        try:
            self._state.conn.backup(save_conn)
        finally:
            save_conn.close()


# db = SqliteMemDatabase(pathlib.Path(__file__).parent.resolve() / "danbooru2023.db")
db = SqliteDatabase(pathlib.Path(__file__).parent.resolve() / "danbooru2023.db")
tag_cache_map = {}


def get_tag_by_id(id):
    if id not in tag_cache_map:
        tag_cache_map[id] = Tag.get_by_id(id)
    return tag_cache_map[id]


class TagListField(TextField, SearchField):
    def db_value(self, value):
        if isinstance(value, str):
            return value
        assert all(isinstance(tag, (Tag, int)) for tag in value)
        return "".join(
            f"${base_repr(tag.id, 36) if isinstance(tag, Tag) else tag}#"
            for tag in value
        )

    def python_value(self, value):
        if value is not None:
            return [
                get_tag_by_id(int(tag, 36)) for tag in value[1:-1].split("#$") if tag
            ]


class EnumField(IntegerField):
    def __init__(self, enum_list, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.enum_list = enum_list
        self.enum_map = {value: index for index, value in enumerate(enum_list)}

    def db_value(self, value):
        if isinstance(value, str):
            return self.enum_map[value]
        assert isinstance(value, int)
        return value

    def python_value(self, value):
        if value is not None:
            return self.enum_list[value]


class BaseModel(Model):
    class Meta:
        database = db


class Post(BaseModel):
    id = IntegerField(primary_key=True)
    created_at = CharField()
    uploader_id = IntegerField()
    source = CharField()
    md5 = CharField(null=True)
    parent_id = IntegerField(null=True)
    has_children = BooleanField()
    is_deleted = BooleanField()
    is_banned = BooleanField()
    pixiv_id = IntegerField(null=True)
    has_active_children = BooleanField()
    bit_flags = IntegerField()
    has_large = BooleanField()
    has_visible_children = BooleanField()

    image_width = IntegerField()
    image_height = IntegerField()
    file_size = IntegerField()
    file_ext = CharField()

    rating = EnumField(["general", "sensitive", "questionable", "explicit"])
    score = IntegerField()
    up_score = IntegerField()
    down_score = IntegerField()
    fav_count = IntegerField()

    file_url = CharField()
    large_file_url = CharField()
    preview_file_url = CharField()

    tag_list = TagListField()
    tag_list_general = TagListField()
    tag_list_artist = TagListField()
    tag_list_character = TagListField()
    tag_list_copyright = TagListField()
    tag_list_meta = TagListField()

    tag_count = IntegerField()
    tag_count_general = IntegerField()
    tag_count_artist = IntegerField()
    tag_count_character = IntegerField()
    tag_count_copyright = IntegerField()
    tag_count_meta = IntegerField()


class PostFTS(FTS5Model):
    class Meta:
        database = db

    tag_list = TagListField()
    tag_list_general = TagListField()
    tag_list_artist = TagListField()
    tag_list_character = TagListField()
    tag_list_copyright = TagListField()
    tag_list_meta = TagListField()


class Tag(BaseModel):
    id = IntegerField(primary_key=True)
    name = CharField(unique=True)
    type = EnumField(["general", "artist", "character", "copyright", "meta"])
    popularity = IntegerField()

    def __str__(self):
        return f"<Tag: {self.name}>"


if __name__ == "__main__":
    from objprint import objprint

    db.connect()
    for index in db.get_indexes("post"):
        print(index)
    post = Post.select().first()
    objprint(model_to_dict(post))
    # db.create_tables([Post, Tag])
    # db.save()
