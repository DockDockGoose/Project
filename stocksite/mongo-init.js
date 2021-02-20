db = db.getSiblingDB("mongodb");

db.createUser(
    {
        user: "root",
        pwd: "dockdockgoose",
        roles: [ { role: "dbOwner", db: "mongodb" }, { role: "userAdminAnyDatabase", db: "mongodb" } ]
    }
)

// db.createUser(
//     {
//         user: "root",
//         pwd: "dockdockgoose",
//         roles: [ { role: "readAnyDatabase", db: "mongodb" }, { role: "dbAdminAnyDatabase", db: "mongodb" }, { role: "userAdminAnyDatabase", db: "mongodb" }]
//     });
