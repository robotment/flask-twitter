'''
All decorator
'''
from functools import wraps
def login_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):    
        '''
        check if user is login, if not redirect to login page
        '''
        if not session.get('username'):
            return redirect(url_for('login'))
        else:
            return f(*args, **kwargs)        
    return decorator

def templated(template=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            template_name = template
            if template_name is None:
                template_name = request.endpoint.replace('.', '/') + '.html'
            ctx = f(*args, **kwargs)
            if ctx is None:
                ctx = {}
            elif not isinstance(ctx, dict):
                return ctx
            return render_template(template_name, **ctx)
        return decorated_function
    return decorator