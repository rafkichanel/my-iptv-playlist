- name: Commit and push changes
  run: |
    git config user.name "github-actions[bot]"
    git config user.email "github-actions[bot]@users.noreply.github.com"
    git add Finalplay.m3u
    if git diff --cached --quiet; then
      echo "No changes detected, skip commit"
    else
      git commit -m "Update playlist otomatis via GitHub Actions"
      git push
    fi
  continue-on-error: true
