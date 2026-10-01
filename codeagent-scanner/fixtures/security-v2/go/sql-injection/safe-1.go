package fixture
import (
"net/http"
"database/sql"
"crypto/tls"
)
func handler(r *http.Request, db *sql.DB) {
name := r.FormValue("name")
db.Query("SELECT * FROM users WHERE name=$1", name)
}
