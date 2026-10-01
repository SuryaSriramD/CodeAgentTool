package fixture
import (
"net/http"
"database/sql"
"crypto/tls"
)
func handler(r *http.Request, db *sql.DB) {
url := r.URL.Query().Get("url")
http.Get(url)
}
