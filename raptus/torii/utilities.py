

def sdir(value):
    biggest = 0
    att = dir(value)
    for i in att:
        if biggest < len(i):
            biggest = len(i)
    for i in att:
        try:
            content = repr(getattr(value,i))[:60]
        except:
            content = '????'
            pass
        print i,' '* (biggest - len(i)), content


def ls(node):
    for i in node.getChildNodes():
        print repr(i)