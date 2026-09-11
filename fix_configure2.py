path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Manager/ProAccessManager.swift"
with open(path, 'r') as f:
    lines = f.readlines()

# Lines 149-154 (0-indexed 148-153) are:
# 149:        }
# 150:    }
# 151:        // Always evaluate immediately...
# 152:        // is reflected...
# 153:        // hasActiveSubscription...
# 154:        AsyncTask { await self.evaluateProStatus() }
# 155:    // MARK: - Pro Status Evaluation

# We want to move lines 151-154 to before line 150 (the closing } of configure)
# Result should be:
# 149:        }
# 150:        // Always evaluate immediately...
# 151:        // is reflected...
# 152:        // hasActiveSubscription...
# 153:        AsyncTask { await self.evaluateProStatus() }
# 154:    }
# 155:    // MARK: - Pro Status Evaluation

# Find the misplaced block by searching for the pattern
target_comment = '        // Always evaluate immediately so a subscription active on another device\n'
target_async   = '        AsyncTask { await self.evaluateProStatus() }\n'
mark_line      = '    // MARK: - Pro Status Evaluation\n'

# Find index of the misplaced comment
idx = None
for i, line in enumerate(lines):
    if line == target_comment:
        idx = i
        break

assert idx is not None, "Could not find misplaced comment"

# The block is lines[idx:idx+4] (comment x3 + AsyncTask)
# The closing } of configure is lines[idx-1]
# We need to move the block to before lines[idx-1]

block = lines[idx:idx+4]  # the 4 lines to move
closing_brace = lines[idx-1]  # '    }\n'

# Remove the block from its current position
del lines[idx:idx+4]

# Now find the closing brace again (it's now at idx-1 still)
# Insert the block before it
lines.insert(idx-1, ''.join(block))

with open(path, 'w') as f:
    f.writelines(lines)
print("done")
