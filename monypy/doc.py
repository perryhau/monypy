from copy import deepcopy

from .meta import DocMeta, DOC_DATA

DOC_INIT_DATA = '__init_data__'

MONGO_ID_KEY = '_id'


class DocBase(dict, metaclass=DocMeta):
    def __getitem__(self, item):
        return self.__dict__[DOC_DATA][item]

    def __setitem__(self, key, value):
        self.__dict__[DOC_DATA][key] = value

    def __delitem__(self, key):
        del self.__dict__[DOC_DATA][key]

    def __contains__(self, item):
        return item in self.__dict__[DOC_DATA]

    def __getattr__(self, item):
        return self.__dict__[DOC_DATA][item]

    def __setattr__(self, key, value):
        self.__dict__[DOC_DATA][key] = value

    def __delattr__(self, item):
        del self.__dict__[DOC_DATA][item]

    def __len__(self):
        return len(self.__dict__[DOC_DATA])

    def __iter__(self):
        return iter(self.__dict__[DOC_DATA])


class Doc(DocBase):
    def __init__(self, *args, **kwargs):
        init_data = args[0] if args else kwargs
        defaults = getattr(self, DOC_INIT_DATA, {})
        defaults.update(init_data)
        self.__dict__[DOC_DATA] = deepcopy(defaults)
        super().__init__()

    async def save(self):
        if MONGO_ID_KEY not in self:
            result = await type(self).manager.insert_one(self.__dict__[DOC_DATA])
            self.__dict__[DOC_DATA][MONGO_ID_KEY] = result.inserted_id
        else:
            await type(self).manager.replace_one({MONGO_ID_KEY: self._id}, self.__dict__[DOC_DATA])

    async def delete(self):
        if MONGO_ID_KEY not in self:
            raise Exception

        await type(self).manager.delete_one({MONGO_ID_KEY: self._id})

        del self._id

    async def refresh(self):
        if MONGO_ID_KEY not in self:
            raise Exception

        result = await type(self).manager.find_one({MONGO_ID_KEY: self._id})
        self.__dict__[DOC_DATA] = result.__dict__[DOC_DATA]
