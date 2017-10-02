# evegen

Utility to generate liveupdates and devtools.raw for evemu.

## Getting it

Check the [releases](https://github.com/THUNDERGROOVE/evegen/releases/)

```
./configure

make
```

I wouldn't recommend `make install` without a prefix.

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

```
#@liveupdate("globalClassMethod", svc.tutorial::TutorialSvc", "GetTutorials")
#@patchinfo("GetTutorials", Disable tutorials whenever accessed.  They cause issues")

def GetTutorials(self):
    import __builtin__
    eve.Message("CustomNotify", {"notify": "Disabling tutorials"})
    __builtin__.settings.Get("Char").Set("ui", "showTutorials", 0)
    eve.Message("CustomNotify", {"notify": "Tutorials disabled!"})
    return {}
```

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

## Devtools

Unlike patches, devtools adds new code to the client.  In some spots in the client, it expects certain code to exist in the client which normally doesn't if you have specific roles.

This can break various things if you're missing said code.

A main devtools files expects a `Bootstrap` function that accepts two arguments.

```
def Bootstrap(a, b):
    ...
```

Inside, you can do pretty much anything you want.  Any code in the Bootstrap function will run.

The only main requirement is that you set the `a.Loader` to a compiled function like so

```
script = "def hello():\n\tprint('Hello World')"
code = compile(script, '<script>', 'exec')
data = marshal.dumps(code)
exec marshal.loads(data) in None, None
a.Loader = hello
```

If you don't do it this way, things get pretty fucky.

Anything used in the Bootstrap function *MUST* be imported in the functions scope.

Any instance of `'hexex::filename.py'` will replace the string with a hex encoded representation of the bytecode.

You can then create a new module with `imp` and dump the code straight into the modules `.__dict__` attribute.

After that is done, you will want to add it to nasty's named object table so it will take into effect globally.  This whole process looks something like this.

```
newclass = "hexex::newclass.py"
code = marshal.loads(newclass.decode("hex"))
NewModule = imp.new_module("NewModule")
exec code in NewModule.__dict, None
nast.nast.RegisterNamedObject(NewModule.NewClass, "form", "NewClass", "devtools.py", globals())
```

## Notes

Sometimes, due to the way scoping turns out, you can't use any imports already imported into the file or sometimes even builtins added by the client.

Generally, just import anything you need in your function.
