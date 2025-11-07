pipeline {
  agent any

  options {
    disableConcurrentBuilds()
    durabilityHint('PERFORMANCE_OPTIMIZED')
  }

  environment {
    VENV           = ".venv"
    PIP_CACHE_DIR  = "C:\\jenkins_cache\\pip"
    DVC_REMOTE     = "C:\\dvc_storage"        // Jenkins ajanının erişebildiği bir yol olmalı
    GIT_USER_NAME  = "jenkins-bot"
    GIT_USER_EMAIL = "jenkins@example.com"
    REPO_URL       = "https://github.com/furkanbuyuky/dvc_jnkns.git"
    BRANCH_NAME    = "main"
  }

  stages {
    stage("Checkout") {
      steps { checkout scm }
    }

    stage("Setup Python & DVC (cached)") {
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
        """
      }
    }

    stage("Sanity: ensure DVC repo") {
      steps {
        bat """
          echo WORKSPACE: %CD%
          dir /a
          if not exist ".dvc" (
            echo [WARN] .dvc not found -> initializing...
            call "%VENV%\\Scripts\\activate"
            dvc init
            git config user.name "%GIT_USER_NAME%"
            git config user.email "%GIT_USER_EMAIL%"
            git add .dvc .gitignore
            git commit -m "CI: init DVC (added by Jenkins)" || echo no changes
          ) else (
            echo [OK] .dvc found.
          )
        """
      }
    }

    stage("Configure DVC remote") {
      steps {
        bat """
          call "%VENV%\\Scripts\\activate"
          dvc remote add -d storage "%DVC_REMOTE%" 2>nul || dvc remote modify storage url "%DVC_REMOTE%"
          dvc remote list
        """
      }
    }

    stage("Track data (if present)") {
      steps {
        bat """
          call "%VENV%\\Scripts\\activate"
          if exist "data\\student_scores.csv" (
            dvc add "data\\student_scores.csv" || echo already tracked
            git config user.name "%GIT_USER_NAME%"
            git config user.email "%GIT_USER_EMAIL%"
            git add "data\\student_scores.csv.dvc" .gitignore
            git commit -m "CI: track student_scores.csv via DVC" || echo no changes
          ) else (
            echo [INFO] data\\student_scores.csv not found, skipping dvc add.
          )
        """
      }
    }

    stage("Train via DVC (if dvc.yaml exists)") {
      steps {
        bat """
          call "%VENV%\\Scripts\\activate"
          if exist "dvc.yaml" (
            echo [RUN] dvc repro
            dvc repro -f
          ) else (
            echo [SKIP] dvc.yaml not found, skipping repro.
          )
        """
      }
    }

    stage("Commit DVC metadata (if changed)") {
      steps {
        bat """
          call "%VENV%\\Scripts\\activate"
          git config user.name "%GIT_USER_NAME%"
          git config user.email "%GIT_USER_EMAIL%"
          git add dvc.yaml dvc.lock .gitignore 2>nul
          git commit -m "CI: update DVC metadata/lock" || echo no changes
        """
      }
    }

    stage("Push Data & Code") {
      steps {
        withCredentials([string(credentialsId: 'git-pat', variable: 'GIT_PAT')]) {
          bat """
            call "%VENV%\\Scripts\\activate"
            echo [PUSH] dvc push
            dvc push

            echo [PUSH] git push
            git remote set-url origin https://%GIT_PAT%@github.com/furkanbuyuky/dvc_jnkns.git
            git push origin HEAD:%BRANCH_NAME%
          """
        }
      }
    }
  }

  // venv'i bilerek silmiyoruz; sonraki build'lerde kurulumu atlar.
  post {
    success {
      echo "Build OK ✅  (venv ve pip cache korundu)"
    }
    failure {
      echo "Build FAILED ❌  (Console Output'u kontrol et)"
    }
  }
}
