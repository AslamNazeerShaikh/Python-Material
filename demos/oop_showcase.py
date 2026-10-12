"""OOP pillars showcase: abstraction, inheritance, polymorphism, encapsulation.

Run from the repo root with ``python demos/oop_showcase.py``. It is kept
free of local imports so both script runs work from the repo root.

Every line carries a teaching comment on purpose (per request). This
file is a demo, not library code, so it trades terseness for
line-by-line explanation. Demos own all ``print()`` output.
"""

# ABC enables abstraction: a base class that cannot be instantiated.
from abc import ABC, abstractmethod


# LibraryItem is abstract: the idea of "lendable", not a concrete thing.
class LibraryItem(ABC):
    """Abstract lendable item. Never instantiated directly."""

    # Class attribute: one shared default slot, overridable per subclass.
    DAILY_RATE: float = 0.0

    # __init__ configures each new object; self is that instance.
    def __init__(self, title: str) -> None:
        # Guard the public boundary: reject empty titles loudly.
        if not title:
            # ValueError (never assert) is the runtime input backstop.
            raise ValueError("title must not be empty")
        # self.title = ... stores per-instance state in obj.__dict__.
        self.title = title

    # @abstractmethod declares what subclasses MUST implement.
    @abstractmethod
    def late_fee(self, days: int) -> float:
        """Return the late fee owed for the given overdue days."""
        # No real body: each subclass supplies its own policy below.
        raise NotImplementedError

    # Concrete method: inherited as-is by every subclass below.
    def describe(self) -> str:
        """Return a one-line human description of the item."""
        # __class__.__name__ stays correct in subclasses (polymorphic).
        return f"{self.__class__.__name__}({self.title!r})"

    # __repr__ controls the developer-facing string of each object.
    def __repr__(self) -> str:
        """Return the unambiguous developer string."""
        # Delegating to describe() keeps a single source of truth.
        return self.describe()


# Book inherits from LibraryItem: an IS-A relationship (inheritance).
class Book(LibraryItem):
    """Physical book with a page count and a cheap daily rate."""

    # Class attribute: overrides the abstract default for books only.
    DAILY_RATE: float = 0.25

    # __init__ extends the parent initializer with book-only state.
    def __init__(self, title: str, pages: int) -> None:
        # super().__init__ builds everything the parent owns (title).
        super().__init__(title)
        # Guard the new parameter before storing it.
        if pages <= 0:
            # Bad values fail here, at construction, not far away later.
            raise ValueError("pages must be > 0")
        # self.pages is per-instance state owned by Book, not the parent.
        self.pages = pages

    # Override: same name/signature as the abstract parent (polymorphism).
    def late_fee(self, days: int) -> float:
        """Return days times the book daily rate."""
        # self.DAILY_RATE reads the subclass class attribute (0.25 here).
        return days * self.DAILY_RATE


# DVD is a second subclass: same interface, different policy/fee.
class DVD(LibraryItem):
    """DVD with a runtime in minutes and a pricier daily rate."""

    # Class attribute: DVDs cost more per overdue day than books.
    DAILY_RATE: float = 1.50

    # __init__ mirrors Book's shape with DVD-owned state instead.
    def __init__(self, title: str, minutes: int) -> None:
        # super().__init__ again: parent setup first, then our own.
        super().__init__(title)
        # Validate the DVD-specific argument before keeping it.
        if minutes <= 0:
            # Same fail-fast rule keeps every constructor honest.
            raise ValueError("minutes must be > 0")
        # Per-instance state living in this DVD's own __dict__.
        self.minutes = minutes

    # Second override of late_fee: the polymorphic call site cannot tell.
    def late_fee(self, days: int) -> float:
        """Return days times the DVD daily rate."""
        # Identical shape to Book's, different rate: polymorphism in action.
        return days * self.DAILY_RATE


# Member shows encapsulation: private state plus a guarded public API.
class Member:
    """Library member holding a private list of borrowed items."""

    # __init__ takes the raw name and builds the member's own state.
    def __init__(self, name: str) -> None:
        # Validate before storing, so no half-built member escapes.
        if not name:
            # Empty names are a caller bug: say so immediately.
            raise ValueError("name must not be empty")
        # self.name is public: reading it directly is fine and expected.
        self.name = name
        # self.__loans is name-mangled (_Member__loans): private by design.
        self.__loans: list[LibraryItem] = []

    # borrow is the ONLY way to grow loans: validation lives here.
    def borrow(self, item: LibraryItem) -> None:
        """Borrow an item, appending it to the private loan list."""
        # isinstance guards the boundary: only lendables may be borrowed.
        if not isinstance(item, LibraryItem):
            # Wrong types fail here instead of corrupting the loan list.
            raise ValueError("item must be a LibraryItem")
        # append() mutates the private list in place and returns None.
        self.__loans.append(item)

    # return_loan removes by title using del on a list index.
    def return_loan(self, title: str) -> None:
        """Return the first loan matching title, else raise ValueError."""
        # Scan with enumerate so we learn each item's index as we go.
        for index, item in enumerate(self.__loans):
            # Compare titles: the first match is the one we return.
            if item.title == title:
                # del removes the item at index; the list shrinks left.
                del self.__loans[index]
                # return ends the method: exactly one copy is returned.
                return
        # No match means a caller bug: fail loudly with the title quoted.
        raise ValueError(f"no loan titled {title!r}")

    # @property exposes derived state read-only (encapsulation, no setter).
    @property
    def loan_count(self) -> int:
        """Return how many items are currently borrowed."""
        # len() of the private list: callers count without touching it.
        return len(self.__loans)

    # Public snapshot: callers see loans without mutating our internals.
    @property
    def loans(self) -> tuple[LibraryItem, ...]:
        """Return an immutable snapshot of the current loans."""
        # tuple() copies outward: appending to it cannot ink our list.
        return tuple(self.__loans)

    # describe gives every member a printable identity for the demo.
    def describe(self) -> str:
        """Return a one-line human description of the member."""
        # f-string formatting keeps the presentation logic in one place.
        return f"Member({self.name!r}, loans={self.loan_count})"


# Librarian inherits Member and extends it: staff are members with power.
class Librarian(Member):
    """Staff member: a Member plus a staff id and louder describe."""

    # __init__ adds staff state on top of everything Member builds.
    def __init__(self, name: str, staff_id: int) -> None:
        # super().__init__ runs Member's init: name validated and stored.
        super().__init__(name)
        # Guard the staff-specific argument before keeping it.
        if staff_id <= 0:
            # Non-positive ids are rejected at construction time.
            raise ValueError("staff_id must be > 0")
        # Per-instance staff state owned by the Librarian layer.
        self.staff_id = staff_id

    # Override that EXTENDS the parent via super() (inheritance + reuse).
    def describe(self) -> str:
        """Return the member line plus the staff badge."""
        # super().describe() reuses Member's formatting, then we append.
        return f"{super().describe()} [staff #{self.staff_id}]"


# main wires objects together and prints each pillar in action.
def main() -> None:
    """Run the OOP showcase, printing each concept as it fires."""
    # Objects: classes are blueprints; these calls build instances.
    book = Book("Dune", 412)
    # Second object of a different subclass, same parent interface.
    dvd = DVD("Seven Samurai", 207)
    # A plain member object and a staff object (subclass of Member).
    amy = Member("amy")
    # Librarian IS-A Member, so anywhere Member fits, jo fits too.
    jo = Librarian("jo", 7)

    # Abstraction proof: instantiating the ABC itself must fail loudly.
    try:
        # LibraryItem has an abstract method, so this call is illegal.
        LibraryItem("ghost")
    # TypeError is the exact signal for "cannot instantiate abstract".
    except TypeError as exc:
        # Print the proof: abstraction is enforced, not just documented.
        print(f"abstract block: {exc}")

    # Encapsulation: borrowing only works through the validating method.
    amy.borrow(book)
    # append() inside borrow grew the private list to length one.
    amy.borrow(dvd)
    # A staff member borrows through the same inherited method.
    jo.borrow(Book("Foundation", 255))

    # Polymorphism: one loop, one call shape, per-class behaviour.
    for item in (book, dvd):
        # late_fee resolves per runtime type: 0.25 vs 1.50 per day.
        print(f"{item.describe()} fee x3d: {item.late_fee(3):.2f}")

    # Same describe() name on Member vs Librarian: override in action.
    print(amy.describe())
    # super().describe() inside Librarian adds the staff badge here.
    print(jo.describe())

    # __dict__ on an OBJECT: the writable bag of instance attributes.
    print(f"amy.__dict__: {amy.__dict__}")
    # __dict__ on a CLASS: a read-only mappingproxy of the namespace.
    print(f"Member.__dict__ type: {type(Member.__dict__).__name__}")
    # The class snapshot holds methods and class-level names, not loans.
    print(f"has describe: {'describe' in Member.__dict__}")

    # del on an ATTRIBUTE: drop state from the instance dict explicitly.
    book.nickname = "spice"
    # Dynamic attributes are legal; the demo adds one to remove it.
    print(f"before del: {hasattr(book, 'nickname')}")
    # del obj.attr removes the entry; later reads raise AttributeError.
    del book.nickname
    # hasattr confirms the removal without raising anything itself.
    print(f"after del: {hasattr(book, 'nickname')}")

    # del on a LIST ITEM via the public return_loan API (encapsulated).
    amy.return_loan("Dune")
    # Only the DVD remains: the count property proves the removal.
    print(f"after return: {amy.describe()}")
    # Snapshot shows the remaining loan without leaking the live list.
    print(f"loans snapshot: {amy.loans}")

    # Inheritance proof: the MRO lists every base in lookup order.
    print(f"Librarian MRO: {[c.__name__ for c in Librarian.__mro__]}")
    # isinstance accepts subclasses: polymorphism's runtime guarantee.
    print(f"jo is Member: {isinstance(jo, Member)}")


# Standard entry guard: running the file executes the demo, importing it.
if __name__ == "__main__":
    # Call main() only as a script; importers get the classes quietly.
    main()
