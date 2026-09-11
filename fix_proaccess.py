#!/usr/bin/env python3
path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Manager/ProAccessManager.swift"
with open(path, 'r') as f:
    content = f.read()

# Fix checkSupabaseProTable
content = content.replace(
    'guard let userID = try? await supabase.auth.session.user.id else { return false }\n        do {\n            let response = try await supabase\n                .from("pro_users")\n                .select("user_id")\n                .eq("user_id", value: userID.uuidString)',
    'guard let userID = currentUserID else { return false }\n        do {\n            let response = try await supabase\n                .from("pro_users")\n                .select("user_id")\n                .eq("user_id", value: userID)'
)

# Fix checkSupabaseProfileFlag
content = content.replace(
    'guard let userID = try? await supabase.auth.session.user.id else { return false }\n        do {\n            struct ProfilePro: Decodable { let is_pro_subscriber: Bool? }\n            let rows: [ProfilePro] = try await supabase\n                .from("profiles")\n                .select("is_pro_subscriber")\n                .eq("id", value: userID.uuidString)',
    'guard let userID = currentUserID else { return false }\n        do {\n            struct ProfilePro: Decodable { let is_pro_subscriber: Bool? }\n            let rows: [ProfilePro] = try await supabase\n                .from("profiles")\n                .select("is_pro_subscriber")\n                .eq("id", value: userID)'
)

with open(path, 'w') as f:
    f.write(content)

# Verify
with open(path, 'r') as f:
    result = f.read()

if 'auth.session.user.id' in result:
    print("STILL HAS OLD CODE")
else:
    print("done - both checks now use currentUserID")
