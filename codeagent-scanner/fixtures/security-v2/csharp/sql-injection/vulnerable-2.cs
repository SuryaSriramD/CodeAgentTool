using System.Data.Common;
using System.Diagnostics;
class Sample { void Handle(DbConnection db, string input) { DbCommand cmd=db.CreateCommand(); cmd.CommandText=$"DELETE FROM users WHERE id={input}"; } }
