pipeline {
  agent any

  options {
    timestamps()
    disableConcurrentBuilds()
    durabilityHint('PERFORMANCE_OPTIMIZED')
  }

  environment {
    VENV           = ".venv"
    PIP_CACHE_DIR  = "C:\\jenkins_cache\\pip"
    DVC_REMOTE     = "C:\\dvc_storage"              // Jenkins ajanında erişilebilir yol
    GIT_USER_NAME  = "Furkan Büyükyozgat"           // istersen değiştir
    GIT_USER_EMAIL = "furkanbuyuky@users.noreply.github.com"
    BRANCH_NAME    = "main"
    REPO_SLUG      = "furkanbuyuky/dvc_jnkns"
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
        bat 'echo [INFO] Workspace: %CD% & dir /a'
      }
    }

    stage('Setup Python & DVC (cached)') {
      steps {
        bat """
          if not exist "%PIP_CACHE_DIR%" mkdir "%PIP_CACHE_DIR%"
          if not exist "%VENV%" (
            echo [SETUP] Creating venv...
            python -m venv "%VENV%"
          ) else (
            echo [SETUP] venv already exists.
          )

          call "%VENV%\\Scripts\\activate"
          python -m pip install --upgrade pip
          python -m pip install --cache-dir "%PIP_CACHE_DIR%" dvc
          dvc --version
          echo [SETUP DONE]
        """
      }
    }

    stage('Ensure DVC repo (.dvc)') {
      steps {
        bat """
          if not exist ".dvc" (
            echo [INIT] .dvc yok -> dvc init
            call "%VENV%\\Scripts\\activate"
            dvc init
            git config user.name "%GIT_USER_NAME%"
            git config user.email "%GIT_USER_EMAIL%"
            git add .dvc .gitignore
            git commit -m "CI: init DVC (by Jenkins)" || echo no changes
          ) else (
            echo [OK] .dvc bulundu.
          )
          dir /a .dvc
        """
      }
    }

    stage('Configure DVC Remote (+commit if changed)') {
      steps {
        bat """
          call "%VENV%\\Scripts\\activate"
          echo [REMOTE] ensure default remote=storage -> %DVC_REMOTE%
          dvc remote add -d storage "%DVC_REMOTE%" 2>nul || dvc remote modify storage url "%DVC_REMOTE%"
          dvc remote list

          rem .dvc/config değiştiyse commit'le
          git config user.name "%GIT_USER_NAME%"
          git config user.email "%GIT_USER_EMAIL%"
          git add .dvc\\config
          git commit -m "CI: update DVC remote config" || echo no changes
          exit /b 0
        """
      }
    }

    stage('Track data (idempotent)') {
      steps {
        bat """
          call "%VENV%\\Scripts\\activate"

          if exist "data\\student_scores.csv" (
            echo [CHECK] is tracked by Git?
            git ls-files --error-unmatch "data\\student_scores.csv" >nul 2>&1
            if %ERRORLEVEL%==0 (
              echo [FIX] Untracking from Git...
              git rm --cached "data\\student_scores.csv"
              if not exist ".gitignore" type NUL > .gitignore
            )

            echo [DVC] dvc add data\\student_scores.csv
            dvc add "data\\student_scores.csv" || echo already tracked

            git config user.name "%GIT_USER_NAME%"
            git config user.email "%GIT_USER_EMAIL%"
            git add "data\\student_scores.csv.dvc" .gitignore
            git commit -m "CI: track student_scores.csv via DVC" || echo no changes
          ) else (
            echo [INFO] data\\student_scores.csv yok, dvc add atlandi.
          )

          exit /b 0
        """
      }
    }

    stage('Train via DVC (repro if dvc.yaml exists)') {
      steps {
        bat """
          call "%VENV%\\Scripts\\activate"
          if exist "dvc.yaml" (
            echo [RUN] dvc repro -f
            dvc repro -f
          ) else (
            echo [SKIP] dvc.yaml yok, repro atlandi.
          )
          exit /b 0
        """
      }
    }

    stage('Commit DVC metadata (if changed)') {
      steps {
        bat """
          call "%VENV%\\Scripts\\activate"
          git config user.name "%GIT_USER_NAME%"
          git config user.email "%GIT_USER_EMAIL%"
          git add dvc.yaml dvc.lock .gitignore 2>nul
          git commit -m "CI: update DVC metadata/lock" || echo no changes
          exit /b 0
        """
      }
    }

    stage('Push Data & Code') {
      steps {
        withCredentials([string(credentialsId: 'git-pat', variable: 'GIT_PAT')]) {
          bat """
            call "%VENV%\\Scripts\\activate"

            echo [PUSH] dvc push
            dvc push

            echo [PUSH] git push
            git remote set-url origin https://%GIT_PAT%@github.com/%REPO_SLUG%.git
            git push origin HEAD:%BRANCH_NAME%

            exit /b 0
          """
        }
      }
    }
  }

  post {
    success { echo "✅ Build OK — venv ve pip cache korundu" }
    failure { echo "❌ Build FAILED — Console Output'u kontrol et" }
  }
}
