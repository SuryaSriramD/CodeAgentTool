package fixture
import (
"net/http"
"database/sql"
"crypto/tls"
)
func handler(r *http.Request, db *sql.DB) {
sort := r.URL.Query().Get("sort")
query := "SELECT * FROM users ORDER BY " + sort
db.QueryRow(query)
}
