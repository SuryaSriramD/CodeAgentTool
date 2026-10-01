package fixture
import (
"net/http"
"database/sql"
"crypto/tls"
)
func handler(r *http.Request, db *sql.DB) {
http.Get("https://service.example/status")
}
