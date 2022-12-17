function deleteUsers() {
    db.runCommand( {   dropUser: "%USER%_usr_ro" } );
    db.runCommand( {   dropUser: "%USER%_sem_ro" } );
    db.runCommand( {   dropUser: "%USER%_int_ro" } );
    db.runCommand( {   dropUser: "%USER%_sess_ro" } );
    db.runCommand( {   dropUser: "%USER%_tech_ro" } );
    db.runCommand( {   dropUser: "%USER%_usr_rw" } );
    db.runCommand( {   dropUser: "%USER%_sem_rw" } );
    db.runCommand( {   dropUser: "%USER%_int_rw" } );
    db.runCommand( {   dropUser: "%USER%_sess_rw" } );
    db.runCommand( {   dropUser: "%USER%_tech_rw" } );
}
function createUsers() {
    db.runCommand( {
        createUser: "%USER%_usr_ro",
        pwd: "%PWD%",
        roles: [
            {role: "read", db:"%USER%_usr"}
        ]
    } );
    db.runCommand( {
        createUser: "%USER%_sem_ro",
        pwd: "%PWD%",
        roles: [
            {role: "read", db:"%USER%_sem"}
        ]
    } );
    db.runCommand( {
        createUser: "%USER%_int_ro",
        pwd: "%PWD%",
        roles: [
            {role: "read", db:"%USER%_int"}
        ]
    } );
    db.runCommand( {
        createUser: "%USER%_sess_ro",
        pwd: "%PWD%",
        roles: [
            {role: "read", db:"%USER%_sess"}
        ]
    } );
    db.runCommand( {
        createUser: "%USER%_tech_ro",
        pwd: "%PWD%",
        roles: [
            {role: "read", db:"%USER%_tech"}
        ]
    } );
    db.runCommand( {
        createUser: "%USER%_usr_rw",
        pwd: "%PWD%",
        roles: [
            {role: "readWrite", db:"%USER%_usr"}
        ]
    } );
    db.runCommand( {
        createUser: "%USER%_sem_rw",
        pwd: "%PWD%",
        roles: [
            {role: "readWrite", db:"%USER%_sem"}
        ]
    } );
    db.runCommand( {
        createUser: "%USER%_int_rw",
        pwd: "%PWD%",
        roles: [
            {role: "readWrite", db:"%USER%_int"}
        ]
    } );
    db.runCommand( {
        createUser: "%USER%_sess_rw",
        pwd: "%PWD%",
        roles: [
            {role: "readWrite", db:"%USER%_sess"}
        ]
    } );
    db.runCommand( {
        createUser: "%USER%_tech_rw",
        pwd: "%PWD%",
        roles: [
            {role: "readWrite", db:"%USER%_tech"}
        ]
    } );
}
{
    deleteUsers();
    createUsers();
}
