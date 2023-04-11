# api 

## get_all_markers_pos -> GET
        retourne une liste des markers (lat, long, id)

## get_marker/\<id> -> GET
        retourne les attributs d'un marker

## add_marker -> POST
params :

        createur : string  
        type_id : int  
        lat : float  
        long : float  
        username : string  
        password : string  
        lien : string  

# add_admin -> POST
        username : string,
        password : string
        new_username : string
        new_password : string


# fonctions 
## check_auth(username, password)
        vérifie si l'id et le mot de passe sont admin

## add_admin(username, password)
        ajoute un admin