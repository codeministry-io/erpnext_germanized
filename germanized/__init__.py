"""Tools for the erpnext_germanized image recipe.

They validate apps.json, derive the image tags of a git ref, compare and move the pinned versions, keep the
app table of the README in step with the pins and summarise a build. Only the standard library is used, so
they run on any Python 3.14 without installing anything.
"""
