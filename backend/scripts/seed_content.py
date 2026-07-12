"""
Idempotent content seed for local/staging environments.

Populates `topics` and `algorithms` with a real, accurate curated DSA
curriculum — not placeholder data. Every complexity figure and problem
statement here is factually correct; `plugin_key` values are the slugs the
Algorithm Engine (Module 3) will register against, so this content becomes
immediately executable once that module ships, with no data migration.

Usage:
    python -m scripts.seed_content
"""
import asyncio

from app.core.database import close_mongo_connection, connect_to_mongo
from app.models.algorithm import Algorithm, Difficulty
from app.models.topic import Topic
from app.models.user import User

TOPICS = [
    dict(name="Arrays & Hashing", slug="arrays-hashing", order=1, icon="grid-3x3",
         description="The building blocks: contiguous storage, hash maps, and the "
                      "trade-offs between lookup speed and memory."),
    dict(name="Two Pointers", slug="two-pointers", order=2, icon="move-horizontal",
         description="Two indices walking an array or string to cut brute-force "
                      "O(n²) scans down to O(n)."),
    dict(name="Sliding Window", slug="sliding-window", order=3, icon="scan",
         description="A window that grows and shrinks over a sequence to track a "
                      "running condition without re-scanning."),
    dict(name="Sorting", slug="sorting", order=4, icon="arrow-up-down",
         description="Comparison and non-comparison sorts, and why their "
                      "complexity floors differ."),
    dict(name="Searching", slug="searching", order=5, icon="search",
         description="Binary search and its many disguises on sorted or "
                      "monotonic search spaces."),
    dict(name="Stacks & Queues", slug="stacks-queues", order=6, icon="layers",
         description="LIFO/FIFO discipline for parsing, monotonic-stack tricks, "
                      "and BFS-style traversal."),
    dict(name="Linked Lists", slug="linked-lists", order=7, icon="link",
         description="Pointer manipulation without random access — reversal, "
                      "cycle detection, merging."),
    dict(name="Trees & BST", slug="trees-bst", order=8, icon="git-branch",
         description="Recursive traversal patterns and the ordering invariant "
                      "that makes BSTs fast.",
         prerequisite_slugs=["linked-lists"]),
    dict(name="Graphs", slug="graphs", order=9, icon="share-2",
         description="BFS, DFS, and the traversal choices that separate "
                      "shortest-path from reachability problems.",
         prerequisite_slugs=["trees-bst"]),
    dict(name="Dynamic Programming", slug="dynamic-programming", order=10, icon="layout-grid",
         description="Recognizing overlapping subproblems and turning "
                      "exponential recursion into polynomial tables.",
         prerequisite_slugs=["sliding-window", "trees-bst"]),
    dict(name="Backtracking", slug="backtracking", order=11, icon="git-fork",
         description="Systematic search with pruning — the recursion tree IS "
                      "the algorithm.",
         prerequisite_slugs=["trees-bst"]),
    dict(name="Greedy", slug="greedy", order=12, icon="trending-up",
         description="Making the locally optimal choice and proving it doesn't "
                      "cost you the global optimum.",
         prerequisite_slugs=["sorting"]),
]

ALGORITHMS = [
    dict(slug="two-sum", title="Two Sum", topic_slug="arrays-hashing", plugin_key="two-sum",
         difficulty=Difficulty.EASY, time_complexity="O(n)", space_complexity="O(n)",
         pattern_tags=["hash-map"], companies=["Amazon", "Google", "Adobe"], estimated_minutes=15,
         statement_md="Given an array of integers `nums` and an integer `target`, return the "
                       "indices of the two numbers that add up to `target`. Assume exactly one "
                       "solution exists and you may not use the same element twice."),
    dict(slug="contains-duplicate", title="Contains Duplicate", topic_slug="arrays-hashing",
         plugin_key="contains-duplicate", difficulty=Difficulty.EASY, time_complexity="O(n)",
         space_complexity="O(n)", pattern_tags=["hash-set"], companies=["Amazon"],
         estimated_minutes=10,
         statement_md="Given an integer array `nums`, return true if any value appears at "
                       "least twice in the array, and false if every element is distinct."),
    dict(slug="valid-palindrome", title="Valid Palindrome", topic_slug="two-pointers",
         plugin_key="valid-palindrome", difficulty=Difficulty.EASY, time_complexity="O(n)",
         space_complexity="O(1)", pattern_tags=["two-pointer"], companies=["Meta", "Microsoft"],
         estimated_minutes=15,
         statement_md="Given a string, determine if it is a palindrome after converting all "
                       "uppercase letters to lowercase and removing all non-alphanumeric "
                       "characters."),
    dict(slug="3sum", title="3Sum", topic_slug="two-pointers", plugin_key="three-sum",
         difficulty=Difficulty.MEDIUM, time_complexity="O(n^2)", space_complexity="O(n)",
         pattern_tags=["two-pointer", "sorting"], companies=["Amazon", "Meta", "Apple"],
         estimated_minutes=30,
         statement_md="Given an integer array `nums`, return all unique triplets "
                       "`[nums[i], nums[j], nums[k]]` such that `i != j != k` and the "
                       "triplet sums to zero."),
    dict(slug="best-time-buy-sell-stock", title="Best Time to Buy and Sell Stock",
         topic_slug="sliding-window", plugin_key="max-subarray-window",
         difficulty=Difficulty.EASY, time_complexity="O(n)", space_complexity="O(1)",
         pattern_tags=["sliding-window"], companies=["Amazon", "Bloomberg"],
         estimated_minutes=15,
         statement_md="Given an array `prices` where `prices[i]` is the price of a stock on "
                       "day `i`, maximize profit by choosing a single day to buy and a later "
                       "day to sell. Return the maximum profit, or 0 if none is possible."),
    dict(slug="longest-substring-without-repeating", title="Longest Substring Without Repeating Characters",
         topic_slug="sliding-window", plugin_key="longest-unique-substring",
         difficulty=Difficulty.MEDIUM, time_complexity="O(n)", space_complexity="O(min(n,m))",
         pattern_tags=["sliding-window", "hash-map"], companies=["Amazon", "Google", "Meta"],
         estimated_minutes=25,
         statement_md="Given a string `s`, find the length of the longest substring without "
                       "repeating characters."),
    dict(slug="bubble-sort", title="Bubble Sort", topic_slug="sorting", plugin_key="bubble-sort",
         difficulty=Difficulty.EASY, time_complexity="O(n^2)", space_complexity="O(1)",
         pattern_tags=["sorting", "comparison-sort"], companies=[], estimated_minutes=10,
         statement_md="Implement bubble sort: repeatedly step through the array, swap "
                       "adjacent elements that are out of order, and repeat until no swaps "
                       "are needed."),
    dict(slug="merge-sort", title="Merge Sort", topic_slug="sorting", plugin_key="merge-sort",
         difficulty=Difficulty.MEDIUM, time_complexity="O(n log n)", space_complexity="O(n)",
         pattern_tags=["sorting", "divide-and-conquer"], companies=["Google"],
         estimated_minutes=25,
         statement_md="Implement merge sort: recursively split the array in half, sort each "
                       "half, then merge the two sorted halves back together."),
    dict(slug="binary-search", title="Binary Search", topic_slug="searching",
         plugin_key="binary-search", difficulty=Difficulty.EASY, time_complexity="O(log n)",
         space_complexity="O(1)", pattern_tags=["binary-search"], companies=["Amazon", "Google"],
         estimated_minutes=10,
         statement_md="Given a sorted array of distinct integers and a target value, return "
                       "the index of the target if found, or -1 otherwise, in O(log n) time."),
    dict(slug="search-rotated-sorted-array", title="Search in Rotated Sorted Array",
         topic_slug="searching", plugin_key="search-rotated-array",
         difficulty=Difficulty.MEDIUM, time_complexity="O(log n)", space_complexity="O(1)",
         pattern_tags=["binary-search"], companies=["Meta", "Amazon", "Microsoft"],
         estimated_minutes=25,
         statement_md="Given a sorted array that has been rotated at an unknown pivot, and a "
                       "target value, return its index, or -1 if not present, in O(log n) time."),
    dict(slug="valid-parentheses", title="Valid Parentheses", topic_slug="stacks-queues",
         plugin_key="valid-parentheses", difficulty=Difficulty.EASY, time_complexity="O(n)",
         space_complexity="O(n)", pattern_tags=["stack"], companies=["Amazon", "Google", "Bloomberg"],
         estimated_minutes=10,
         statement_md="Given a string containing just the characters '(', ')', '{', '}', "
                       "'[' and ']', determine if the input string has valid, properly "
                       "nested and matched brackets."),
    dict(slug="min-stack", title="Min Stack", topic_slug="stacks-queues", plugin_key="min-stack",
         difficulty=Difficulty.MEDIUM, time_complexity="O(1) per op", space_complexity="O(n)",
         pattern_tags=["stack", "design"], companies=["Amazon"], estimated_minutes=20,
         statement_md="Design a stack that supports push, pop, top, and retrieving the "
                       "minimum element, all in O(1) time."),
    dict(slug="reverse-linked-list", title="Reverse Linked List", topic_slug="linked-lists",
         plugin_key="reverse-linked-list", difficulty=Difficulty.EASY, time_complexity="O(n)",
         space_complexity="O(1)", pattern_tags=["linked-list"], companies=["Amazon", "Meta", "Apple"],
         estimated_minutes=15,
         statement_md="Given the head of a singly linked list, reverse the list in place and "
                       "return the new head."),
    dict(slug="linked-list-cycle", title="Linked List Cycle", topic_slug="linked-lists",
         plugin_key="linked-list-cycle", difficulty=Difficulty.EASY, time_complexity="O(n)",
         space_complexity="O(1)", pattern_tags=["linked-list", "two-pointer"], companies=["Amazon"],
         estimated_minutes=15,
         statement_md="Given the head of a linked list, determine if the list has a cycle "
                       "using O(1) extra space (Floyd's tortoise and hare)."),
    dict(slug="invert-binary-tree", title="Invert Binary Tree", topic_slug="trees-bst",
         plugin_key="invert-binary-tree", difficulty=Difficulty.EASY, time_complexity="O(n)",
         space_complexity="O(h)", pattern_tags=["tree", "dfs"], companies=["Google"],
         estimated_minutes=10,
         statement_md="Given the root of a binary tree, invert the tree (swap every left and "
                       "right child) and return its root."),
    dict(slug="validate-bst", title="Validate Binary Search Tree", topic_slug="trees-bst",
         plugin_key="validate-bst", difficulty=Difficulty.MEDIUM, time_complexity="O(n)",
         space_complexity="O(h)", pattern_tags=["tree", "dfs", "bst"], companies=["Amazon", "Meta"],
         estimated_minutes=25,
         statement_md="Given the root of a binary tree, determine if it is a valid binary "
                       "search tree, where every node's value must fall within the range "
                       "established by its ancestors."),
    dict(slug="number-of-islands", title="Number of Islands", topic_slug="graphs",
         plugin_key="number-of-islands", difficulty=Difficulty.MEDIUM, time_complexity="O(m*n)",
         space_complexity="O(m*n)", pattern_tags=["graph", "bfs", "dfs"],
         companies=["Amazon", "Google", "Meta"], estimated_minutes=25,
         statement_md="Given an `m x n` 2D grid of '1's (land) and '0's (water), return the "
                       "number of islands, where an island is surrounded by water and formed "
                       "by connecting adjacent land horizontally or vertically."),
    dict(slug="course-schedule", title="Course Schedule", topic_slug="graphs",
         plugin_key="course-schedule", difficulty=Difficulty.MEDIUM, time_complexity="O(V+E)",
         space_complexity="O(V+E)", pattern_tags=["graph", "topological-sort"],
         companies=["Amazon", "Google"], estimated_minutes=30,
         statement_md="Given `numCourses` and a list of prerequisite pairs, determine if it "
                       "is possible to finish all courses (i.e., the prerequisite graph "
                       "contains no cycle)."),
    dict(slug="climbing-stairs", title="Climbing Stairs", topic_slug="dynamic-programming",
         plugin_key="climbing-stairs", difficulty=Difficulty.EASY, time_complexity="O(n)",
         space_complexity="O(1)", pattern_tags=["dp", "fibonacci"], companies=["Amazon", "Adobe"],
         estimated_minutes=15,
         statement_md="You are climbing a staircase with `n` steps, taking 1 or 2 steps at a "
                       "time. Return the number of distinct ways to reach the top."),
    dict(slug="coin-change", title="Coin Change", topic_slug="dynamic-programming",
         plugin_key="coin-change", difficulty=Difficulty.MEDIUM, time_complexity="O(n*amount)",
         space_complexity="O(amount)", pattern_tags=["dp", "unbounded-knapsack"],
         companies=["Amazon", "Google", "Uber"], estimated_minutes=30,
         statement_md="Given coin denominations and a target amount, return the fewest number "
                       "of coins needed to make up that amount, or -1 if it cannot be made."),
    dict(slug="subsets", title="Subsets", topic_slug="backtracking", plugin_key="subsets",
         difficulty=Difficulty.MEDIUM, time_complexity="O(n*2^n)", space_complexity="O(n*2^n)",
         pattern_tags=["backtracking"], companies=["Meta", "Amazon"], estimated_minutes=20,
         statement_md="Given an integer array of unique elements, return all possible subsets "
                       "(the power set)."),
    dict(slug="jump-game", title="Jump Game", topic_slug="greedy", plugin_key="jump-game",
         difficulty=Difficulty.MEDIUM, time_complexity="O(n)", space_complexity="O(1)",
         pattern_tags=["greedy"], companies=["Amazon", "Google"], estimated_minutes=20,
         statement_md="Given an array where each element represents your maximum jump length "
                       "from that position, determine if you can reach the last index "
                       "starting from index 0."),
]


async def seed() -> None:
    await connect_to_mongo([User, Topic, Algorithm])

    slug_to_id = {}
    for topic_data in TOPICS:
        prereq_slugs = topic_data.pop("prerequisite_slugs", [])
        existing = await Topic.find_one(Topic.slug == topic_data["slug"])
        if existing:
            slug_to_id[topic_data["slug"]] = existing.id
            print(f"topic exists: {topic_data['slug']}")
            continue
        topic = Topic(**topic_data, prerequisite_ids=[])
        await topic.insert()
        slug_to_id[topic_data["slug"]] = topic.id
        topic_data["_prereq_slugs"] = prereq_slugs
        print(f"created topic: {topic_data['slug']}")

    # Second pass: resolve prerequisite slugs to ids now that every topic exists.
    for topic_data in TOPICS:
        prereq_slugs = topic_data.pop("_prereq_slugs", [])
        if not prereq_slugs:
            continue
        topic = await Topic.get(slug_to_id[topic_data["slug"]])
        topic.prerequisite_ids = [slug_to_id[s] for s in prereq_slugs]
        await topic.save()

    for order, algo_data in enumerate(ALGORITHMS):
        existing = await Algorithm.find_one(Algorithm.slug == algo_data["slug"])
        if existing:
            print(f"algorithm exists: {algo_data['slug']}")
            continue
        topic_slug = algo_data.pop("topic_slug")
        algorithm = Algorithm(**algo_data, topic_id=slug_to_id[topic_slug], order=order)
        await algorithm.insert()
        print(f"created algorithm: {algo_data['slug']}")

    await close_mongo_connection()
    print("Seed complete.")


if __name__ == "__main__":
    asyncio.run(seed())
