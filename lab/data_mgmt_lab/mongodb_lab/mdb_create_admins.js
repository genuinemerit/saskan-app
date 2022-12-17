function dropAdmins() {
   db.runCommand( {   dropUser: "%USER%_user_admin" } );
   db.runCommand( {   dropUser: "%USER%_db_admin" } );
   db.runCommand( {   dropUser: "%USER%_owner" }  );
}
function createDbAdmin() {
    db.runCommand({
        createUser: "%USER%_db_admin",
        pwd: "%PWD%",
        roles: [{
            role: "dbAdminAnyDatabase",
            db: "admin"
        }]
    });
};
function createUserAdmin() {
    db.runCommand({
        createUser: "%USER%_user_admin",
        pwd: "%PWD%",
        roles: [{
            role: "userAdminAnyDatabase",
            db: "admin"
        }]
    });
};
function createDbOwner() {
    db.runCommand({
        createUser: "%USER%_owner",
        pwd: "%PWD%",
        roles: [{
            role: "dbOwner",
            db: "%USER%_usr"
        }, {
            role: "dbOwner",
            db: "%USER%_sem"
        }, {
            role: "dbOwner",
            db: "%USER%_int"
        }, {
            role: "dbOwner",
            db: "%USER%_sess"
        }, {
            role: "dbOwner",
            db: "%USER%_tech"
        }, {
            role: "read",
            db: "admin"
        }]
    });
};
{
    dropAdmins();
    createDbAdmin();
    createUserAdmin();
    createDbOwner();
}
