package fixture
import (
"net/http"
"database/sql"
"crypto/tls"
)
func handler(r *http.Request, db *sql.DB) {
cfg := &tls.Config{MinVersion:tls.VersionTLS13}
_ = cfg
}
