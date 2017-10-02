#### evengen

Utility to generate liveupdates and devtools.raw for evemu.

## argument info

Generate a devtools.raw file
`./evegen -dev <devtools file>`
The argument is optional

Apply patches to the database
`./evegen -patch <username> <password> <db>`
All arguments required

Do a test run of the patches without writing to the database
`./evegen -test` 

## patch files

Patch files essentially overwrite specific functions in the EVE client.

The simplest example is the patch for disable the tutorials.

`
#@liveupdate("globalClassMethod", svc.tutorial::TutorialSvc", "GetTutorials")
#@patchinfo("GetTutorials", Disable tutorials whenever accessed.  They cause issues")

def GetTutorials(self):
    import __builtin__
    eve.Message("CustomNotify", {"notify": "Disabling tutorials"})
    __builtin__.settings.Get("Char").Set("ui", "showTutorials", 0)
    eve.Message("CustomNotify", {"notify": "Tutorials disabled!"})
    return {}
`

You can see the decorator like annotations at the beginging of the file.  They can exist anywhere in the file but it's good practice to leave them in the begining.

The first one is `liveupdate` it always has three arguments.

This portion is limited as it's been awhile since I've worked with patches.

1. patch type.
2. Where clause. 
3. Identifier of what you're patching

Generally, you can do anything with `globalClassMethod` patch type.
The where clause for that is going to be 
`<destination package>.<class name>::<instance name>`

The second annotation is `patchinfo`

It requires two arguments as follows

1. Name of the function in the patch file you're using to patch the original
2. Description

The description is only in the DB, and afaik isn't even sent to the client.

## Notes

Sometimes, due to the way scoping turns out, you can't use any imports already imported into the file or sometimes even builtins added by the client.

Generally, just import anything you need in your function.
