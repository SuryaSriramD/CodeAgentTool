using System.Data.Common;
using System.Diagnostics;
class Sample { void Handle(DbConnection db, string input) { var cmd=db.CreateCommand(); cmd.CommandText="SELECT * FROM users WHERE name="+input; } }
