// var db = connect("mongodb://root:dockdockgoose@localhost:27017/admin");

// db.auth('root', 'dockdockgoose'); 

// db = db.getSiblingDB('stocksite_db_prod'); 

// db.createUser(
//     { 
//         user: 'root', 
//         pwd: 'dockdockgoose', 
//         roles: [{ role: 'dbOwner', db: 'stocksite_db_prod' }, { role: "userAdminAnyDatabase", db: '$stocksite_db_prod' }]
//     }
    
// );

db = db.getSiblingDB("stocksite_db_prod");

db.createUser(
    {
        user: "root",
        pwd: "dockdockgoose",
        roles: [ { role: "dbOwner", db: "stocksite_db_prod" }, { role: "readWrite", db: "stocksite_db_prod" } ]
    }
)

// Update this file to create a non root/admin MongoDB user for security in prouction.
// db.createUser(
//     {
//         user: "stocksiteUser",
//         pwd: "dockdockgoose",
//         roles: [ { role: "readAnyDatabase", db: "stocksite_db_prod" }, { role: "dbAdminAnyDatabase", db: "stocksite_db_prod" }, { role: "userAdminAnyDatabase", db: "stocksite_db_prod" }]
//     });
