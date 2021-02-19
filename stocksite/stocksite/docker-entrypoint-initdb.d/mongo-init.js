// db.createUser(
//     {
//         user: "<user for database which shall be created>",
//         pwd: "<password of user>",
//         roles: [
//             {
//                 role: "readWrite",
//                 db: "<database to create>"
//             }
//         ]
//     }
// );

db = db.getSiblingDB("mongodb");

db.createUser(
    {
        user: "root",
        pwd: "dockdockgoose",
        roles: [ { role: "dbOwner", db: "mongodb" }, { role: "userAdminAnyDatabase", db: "mongodb" } ]
    }
)

db.createCollection('users');

db.article.drop();

db.article.save( {
    title : "this is my title" , 
    author : "bob" , 
    posted : new Date(1079895594000) , 
    pageViews : 5 , 
    tags : [ "fun" , "good" , "fun" ] ,
    comments : [ 
        { author :"joe" , text : "this is cool" } , 
        { author :"sam" , text : "this is bad" } 
    ],
    other : { foo : 5 }
});


// db.createUser(
//     {
//         user: "root",
//         pwd: "dockdockgoose",
//         roles: [ { role: "readAnyDatabase", db: "mongodb" }, { role: "dbAdminAnyDatabase", db: "mongodb" }, { role: "userAdminAnyDatabase", db: "mongodb" }]
//     });
