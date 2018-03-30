actor.log( "in client conf: %s" % actor.pw_name())
if actor.pw_name() == "client2" :
    actor.pw_set_timeout(1)
    
