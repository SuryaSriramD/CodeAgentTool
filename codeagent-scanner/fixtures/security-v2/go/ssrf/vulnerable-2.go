package fixture
import (
"net/http"
"database/sql"
"crypto/tls"
)
func handler(r *http.Request, db *sql.DB) {
host := r.FormValue("host")
http.Get("http://"+host)
}
