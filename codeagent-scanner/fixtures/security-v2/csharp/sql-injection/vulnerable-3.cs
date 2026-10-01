using System.Data.Common;
using System.Diagnostics;
class Sample { void Handle(DbConnection db, string input) { var command=db.CreateCommand(); var sql="SELECT * FROM users ORDER BY "+input; command.CommandText=sql; } }
