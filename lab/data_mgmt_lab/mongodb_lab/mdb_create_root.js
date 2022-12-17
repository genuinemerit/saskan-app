function dropRoot() {
   db.runCommand( {   dropUser: "%USER%" } );
}
function createRoot() {
    db.runCommand({
        createUser: "%USER%",
        pwd: "%PWD%",
        roles: [{
            role: "root",
            db: "admin"
        }]
    });
};
{
    dropRoot();
    createRoot();
}
