from __future__ import print_function
import os
import sys
import functools

# get the db directory
#os.environ

def compare_filenames(fname1, fname2):
    """
    Compares two migration filenames.

    >>> compare_filenames("migration_20161218_1.sql", "migration_20161218_2.sql")
    1

    >>> compare_filenames("migration_20161219_1.sql", "migration_20161218_1.sql")
    -1

    >>> compare_filenames("migration_20161218_1.sql", "migration_20161218_2.sql")
    1

    >>> compare_filenames("migration_20161218_2.sql","migration_20161218_1.sql")
    -1

    >>> compare_filename("migration_20161218_1.sql, migration_20161218_1_1.sql")
    1

    >>> compare_filename("migration_20161218_1_1.sql", "migration_20161218_1.sql")
    -1

    """

    trunc1 = fname1[:fname1.index(".sql")]
    trunc2 = fname2[:fname2.index(".sql")]

    fields1 = trunc1.split("_")[1:]
    fields2 = trunc2.split("_")[1:]

    if len(fields1) != len(fields2):
        lf1 = len(fields1)
        lf2 = len(fields2)

        l = min(lf1, lf2)

        for i in range(l):
            comp1 = fields1[i]
            comp2 = fields2[i]

            if comp1 != comp2:
                if max(comp1, comp2) == comp1:
                    return 1
                else:
                    return -1

        if l == lf1:
            return -1
        else:
            return 1

    else:
        for i in range(len(fields1)):
            comp1 = fields1[i]
            comp2 = fields2[i]

            if comp1 != comp2:
                if max(comp1, comp2) == comp1:
                    return 1
                else:
                    return -1

if __name__ == '__main__':
    dirname = sys.argv[1]
    dirlist = os.listdir(dirname)

    dirlist_filtered = list(filter(lambda s: s.startswith("migration"), dirlist))

    dirlist_sorted = sorted(dirlist_filtered, key=functools.cmp_to_key(compare_filenames))

    for i in dirlist_sorted:
        print(i)
        os.system("psql -f %s" % (dirname + i))
        print("Migration complete: %s" % i)
