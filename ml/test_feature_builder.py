from feature_builder import build_ml_features


sample = {

    "src_port": 54321,
    "dst_port": 80,

    "proto": "tcp",
    "service": "http",

    "duration": 1.5,

    "src_bytes": 1500,
    "dst_bytes": 3000,

    "conn_state": "SF",

    "missed_bytes": 0,

    "src_pkts": 20,
    "src_ip_bytes": 1800,

    "dst_pkts": 25,
    "dst_ip_bytes": 3300,

    "dns_qclass": 1,
    "dns_qtype": 1,
    "dns_rcode": 0,

    "dns_AA": False,
    "dns_RD": True,
    "dns_RA": True,
    "dns_rejected": False,

    "ssl_version": "TLSv12",

    "ssl_cipher": "TLS_AES_128_GCM_SHA256",

    "ssl_resumed": False,
    "ssl_established": True,

    "http_trans_depth": 1,

    "http_method": "GET",

    "http_version": "1.1",

    "http_request_body_len": 0,

    "http_response_body_len": 2000,

    "http_status_code": 200
}


features = build_ml_features(sample)


print("=" * 70)
print("FEATURE BUILDER TEST")
print("=" * 70)

print("\nFeature shape:")
print(features.shape)

print("\nNumber of features:")
print(len(features.columns))

print("\nMissing values:")
print(features.isnull().sum().sum())

print("\nFirst features:")
print(features.iloc[0].head(15))

print("\nFeature builder test completed.")