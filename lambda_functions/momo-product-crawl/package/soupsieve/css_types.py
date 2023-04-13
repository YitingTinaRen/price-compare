"""CSS selector structure items."""
import copyreg
from .pretty import pretty
from typing import Any, Type, Tuple, Union, Dict, Iterator, Hashable, Optional, Pattern, Iterable, Mapping

__all__ = (
    'Selector',
    'SelectorNull',
    'SelectorTag',
    'SelectorAttribute',
    'SelectorContains',
    'SelectorNth',
    'SelectorLang',
    'SelectorList',
    'Namespaces',
    'CustomSelectors'
)


SEL_EMPTY = 0x1
SEL_ROOT = 0x2
SEL_DEFAULT = 0x4
SEL_INDETERMINATE = 0x8
SEL_SCOPE = 0x10
SEL_DIR_LTR = 0x20
SEL_DIR_RTL = 0x40
SEL_IN_RANGE = 0x80
SEL_OUT_OF_RANGE = 0x100
SEL_DEFINED = 0x200
SEL_PLACEHOLDER_SHOWN = 0x400


class Immutable:
    """Immutable."""

    __slots__: Tuple[str, ...] = ('_hash',)

    _hash: int

    def __init__(self, **kwargs: Any) -> None:
        """Initialize."""

        temp = []
        for k, v in kwargs.items():
            temp.append(type(v))
            temp.append(v)
            super(Immutable, self).__setattr__(k, v)
        super(Immutable, self).__setattr__('_hash', hash(tuple(temp)))

    @classmethod
    def __base__(cls) -> "Type[Immutable]":
        """Get base class."""

        return cls

    def __eq__(self, other: Any) -> bool:
        """Equal."""

        return (isinstance(other, self.__base__()) and all([getattr(
            other, key) == getattr(self, key) for key in self.__slots__ if key != '_hash']))

    def __ne__(self, other: Any) -> bool:
        """Equal."""

        return (not isinstance(other, self.__base__()) or any([getattr(
            other, key) != getattr(self, key) for key in self.__slots__ if key != '_hash']))

    def __hash__(self) -> int:
        """Hash."""

        return self._hash

    def __setattr__(self, name: str, value: Any) -> None:
        """Prevent mutability."""

        raise AttributeError(
            "'{}' is immutable".format(
                self.__class__.__name__))

    def __repr__(self) -> str:  # pragma: no cover
        """Representation."""

        return "{}({})".format(self.__class__.__name__, ', '.join(
            ["{}={!r}".format(k, getattr(self, k)) for k in self.__slots__[:-1]]))

    __str__ = __repr__

    def pretty(self) -> None:  # pragma: no cover
        """Pretty print."""

        print(pretty(self))


class ImmutableDict(Mapping[Any, Any]):
    """Hashable, immutable dictionary."""

    def __init__(
        self,
        arg: Union[Dict[Any, Any], Iterable[Tuple[Any, Any]]]
    ) -> None:
        """Initialize."""

        self._validate(arg)
        self._d = dict(arg)
        self._hash = hash(tuple([(type(x), x, type(y), y)
                          for x, y in sorted(self._d.items())]))

    def _validate(self, arg: Union[Dict[Any, Any],
                  Iterable[Tuple[Any, Any]]]) -> None:
        """Validate arguments."""

        if isinstance(arg, dict):
            if not all([isinstance(v, Hashable) for v in arg.values()]):
                raise TypeError(
                    '{} values must be hashable'.format(
                        self.__class__.__name__))
        elif not all([isinstance(k, Hashable) and isinstance(v, Hashable) for k, v in arg]):
            raise TypeError(
                '{} values must be hashable'.format(
                    self.__class__.__name__))

    def __iter__(self) -> Iterator[Any]:
        """Iterator."""

        return iter(self._d)

    def __len__(self) -> int:
        """Length."""

        return len(self._d)

    def __getitem__(self, key: Any) -> Any:
        """Get item: `namespace['key']`."""

        return self._d[key]

    def __hash__(self) -> int:
        """Hash."""

        return self._hash

    def __repr__(self) -> str:  # pragma: no cover
        """Representation."""

        return "{!r}".format(self._d)

    __str__ = __repr__


class Namespaces(ImmutableDict):
    """Namespaces."""

    def __init__(self, arg: Union[Dict[str, str],
                 Iterable[Tuple[str, str]]]) -> None:
        """Initialize."""

        super().__init__(arg)

    def _validate(self, arg: Union[Dict[str, str],
                  Iterable[Tuple[str, str]]]) -> None:
        """Validate arguments."""

        if isinstance(arg, dict):
            if not all([isinstance(v, str) for v in arg.values()]):
                raise TypeError(
                    '{} values must be hashable'.format(
                        self.__class__.__name__))
        elif not all([isinstance(k, str) and isinstance(v, str) for k, v in arg]):
            raise TypeError(
                '{} keys and values must be Unicode strings'.format(
                    self.__class__.__name__))


class CustomSelectors(ImmutableDict):
    """Custom selectors."""

    def __init__(self, arg: Union[Dict[str, str],
                 Iterable[Tuple[str, str]]]) -> None:
        """Initialize."""

        super().__init__(arg)

    def _validate(self, arg: Union[Dict[str, str],
                  Iterable[Tuple[str, str]]]) -> None:
        """Validate arguments."""

        if isinstance(arg, dict):
            if not all([isinstance(v, str) for v in arg.values()]):
                raise TypeError(
                    '{} values must be hashable'.format(
                        self.__class__.__name__))
        elif not all([isinstance(k, str) and isinstance(v, str) for k, v in arg]):
            raise TypeError(
                '{} keys and values must be Unicode strings'.format(
                    self.__class__.__name__))


class Selector(Immutable):
    """Selector."""

    __slots__ = (
        'tag', 'ids', 'classes', 'attributes', 'nth', 'selectors',
        'relation', 'rel_type', 'contains', 'lang', 'flags', '_hash'
    )

    tag: Optional['SelectorTag']
    ids: Tuple[str, ...]
    classes: Tuple[str, ...]
    attributes: Tuple['SelectorAttribute', ...]
    nth: Tuple['SelectorNth', ...]
    selectors: Tuple['SelectorList', ...]
    relation: 'SelectorList'
    rel_type: Optional[str]
    contains: Tuple['SelectorContains', ...]
    lang: Tuple['SelectorLang', ...]
    flags: int

    def __init__(
        self,
        tag: Optional['SelectorTag'],
        ids: Tuple[str, ...],
        classes: Tuple[str, ...],
        attributes: Tuple['SelectorAttribute', ...],
        nth: Tuple['SelectorNth', ...],
        selectors: Tuple['SelectorList', ...],
        relation: 'SelectorList',
        rel_type: Optional[str],
        contains: Tuple['SelectorContains', ...],
        lang: Tuple['SelectorLang', ...],
        flags: int
    ):
        """Initialize."""

        super().__init__(
            tag=tag,
            ids=ids,
            classes=classes,
            attributes=attributes,
            nth=nth,
            selectors=selectors,
            relation=relation,
            rel_type=rel_type,
            contains=contains,
            lang=lang,
            flags=flags
        )


class SelectorNull(Immutable):
    """Null Selector."""

    def __init__(self) -> None:
        """Initialize."""

        super().__init__()


class SelectorTag(Immutable):
    """Selector tag."""

    __slots__ = ("name", "prefix", "_hash")

    name: str
    prefix: Optional[str]

    def __init__(self, name: str, prefix: Optional[str]) -> None:
        """Initialize."""

        super().__init__(name=name, prefix=prefix)


class SelectorAttribute(Immutable):
    """Selector attribute rule."""

    __slots__ = ("attribute", "prefix", "pattern", "xml_type_pattern", "_hash")

    attribute: str
    prefix: str
    pattern: Optional[Pattern[str]]
    xml_type_pattern: Optional[Pattern[str]]

    def __init__(
        self,
        attribute: str,
        prefix: str,
        pattern: Optional[Pattern[str]],
        xml_type_pattern: Optional[Pattern[str]]
    ) -> None:
        """Initialize."""

        super().__init__(
            attribute=attribute,
            prefix=prefix,
            pattern=pattern,
            xml_type_pattern=xml_type_pattern
        )


class SelectorContains(Immutable):
    """Selector contains rule."""

    __slots__ = ("text", "own", "_hash")

    text: Tuple[str, ...]
    own: bool

    def __init__(self, text: Iterable[str], own: bool) -> None:
        """Initialize."""

        super().__init__(text=tuple(text), own=own)


class SelectorNth(Immutable):
    """Selector nth type."""

    __slots__ = ("a", "n", "b", "of_type", "last", "selectors", "_hash")

    a: int
    n: bool
    b: int
    of_type: bool
    last: bool
    selectors: 'SelectorList'

    def __init__(
        self,
        a: int,
        n: bool,
        b: int,
        of_type: bool,
        last: bool,
            selectors: 'SelectorList') -> None:
        """Initialize."""

        super().__init__(
            a=a,
            n=n,
            b=b,
            of_type=of_type,
            last=last,
            selectors=selectors
        )


class SelectorLang(Immutable):
    """Selector language rules."""

    __slots__ = ("languages", "_hash",)

    languages: Tuple[str, ...]

    def __init__(self, languages: Iterable[str]):
        """Initialize."""

        super().__init__(languages=tuple(languages))

    def __iter__(self) -> Iterator[str]:
        """Iterator."""

        return iter(self.languages)

    def __len__(self) -> int:  # pragma: no cover
        """Length."""

        return len(self.languages)

    def __getitem__(self, index: int) -> str:  # pragma: no cover
        """Get item."""

        return self.languages[index]


class SelectorList(Immutable):
    """Selector list."""

    __slots__ = ("selectors", "is_not", "is_html", "_hash")

    selectors: Tuple[Union['Selector', 'SelectorNull'], ...]
    is_not: bool
    is_html: bool

    def __init__(
        self,
        selectors: Optional[Iterable[Union['Selector', 'SelectorNull']]] = None,
        is_not: bool = False,
        is_html: bool = False
    ) -> None:
        """Initialize."""

        super().__init__(
            selectors=tuple(selectors) if selectors is not None else tuple(),
            is_not=is_not,
            is_html=is_html
        )

    def __iter__(self) -> Iterator[Union['Selector', 'SelectorNull']]:
        """Iterator."""

        return iter(self.selectors)

    def __len__(self) -> int:
        """Length."""

        return len(self.selectors)

    def __getitem__(self, index: int) -> Union['Selector', 'SelectorNull']:
        """Get item."""

        return self.selectors[index]


def _pickle(p: Any) -> Any:
    return p.__base__(), tuple([getattr(p, s) for s in p.__slots__[:-1]])


def pickle_register(obj: Any) -> None:
    """Allow object to be pickled."""

    copyreg.pickle(obj, _pickle)


pickle_register(Selector)
pickle_register(SelectorNull)
pickle_register(SelectorTag)
pickle_register(SelectorAttribute)
pickle_register(SelectorContains)
pickle_register(SelectorNth)
pickle_register(SelectorLang)
pickle_register(SelectorList)
