"""Demo runner. This is the only place with print() output."""

from python_material.arrays.custom_sorter import sort_with_bubble_sort
from python_material.arrays.second_largest import find_second_largest
from python_material.common import SortDirection
from python_material.strings.vowel_counter import count_unique_vowels


def main() -> None:
    """Run the available demos."""
    print(f"Second largest: {find_second_largest([5, 1, 5, 3])}")
    print(f"Sorted: {sort_with_bubble_sort([3, 1, 2], SortDirection.ASCENDING)}")
    print(f"Unique vowels: {count_unique_vowels('Minneapolis')}")


if __name__ == "__main__":
    main()
