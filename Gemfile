source "https://rubygems.org"

# GitHub Pages 레거시 빌드가 프로덕션에서 쓰는 의존성 세트.
# 로컬에서는 이 Gemfile로 동일 버전을 재현한다.
gem "github-pages", group: :jekyll_plugins

# Ruby 3.x에서 webrick이 표준 라이브러리에서 빠졌다. Jekyll 3.x `serve`가 필요로 한다.
# GitHub Pages 레거시 빌드는 Gemfile을 무시하므로 로컬 개발 전용이며 프로덕션에 영향 없다.
gem "webrick"