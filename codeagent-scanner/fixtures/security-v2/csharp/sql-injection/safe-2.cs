using System.Data.Common;
using System.Diagnostics;
class Sample { void Handle(DbConnection db, string input) { var command=db.CreateCommand(); command.CommandText="SELECT count(*) FROM users"; } }
