# encoding: utf-8

def validate_dict(h,*args):
    for arg in args:
        if type(h).__name__=='dict' and type(arg).__name__=='list':
            for key in arg:
                if key not in h or h[key] is None:
                    return False
        elif type(h).__name__=='dict' and type(arg).__name__=='dict':
            for k in arg:
                if k not in h or h[k] is None:
                    return False
                v=arg[k]
                val=h[k]
                ans=validate_dict(val,v)
                if ans==False:
                    return False
        elif type(arg).__name__=='str':
            if arg!=h:
                return False
        else:
            return False
    return True
    
def parse_dict(h,p,validate=None,default=None):
    if type(h).__name__!='dict':
        return default
    if validate is not None and validate_dict(h,validate)==False:
        return default
    if type(p).__name__=='str':
        if p in h and h[p] is not None:
            return h[p]
        else:
            return default
    elif type(p).__name__=='dict':
        for k in p:
            if k not in h or h[k] is None:
                return default
            else:
                val=h[k]
                v=p[k]
                return parse_dict(val,v,default=default)
        return default
