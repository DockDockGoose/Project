db = db.getSiblingDB("stocksite_db_dev");

db.createUser(
    {
        user: "root",
        pwd: "dockdockgoose",
        roles: [ { role: "dbOwner", db: "stocksite_db_dev" }, { role: "userAdminAnyDatabase", db: "stocksite_db_dev" } ]
    }
)

// db.createUser(
//     {
//         user: "root",
//         pwd: "dockdockgoose",
//         roles: [ { role: "readAnyDatabase", db: "mongodb" }, { role: "dbAdminAnyDatabase", db: "mongodb" }, { role: "userAdminAnyDatabase", db: "mongodb" }]
//     });
