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
    DVC_REMOTE     = "C:\\dvc_storage"                  // Jenkins ajanında erişilebilir yol
    GIT_USER_NAME  = "jenkins-bot"
    GIT_USER_EMAIL = "jenkins@example.com"
    REPO_URL       = "https://github.com/furkanbuyuky/dvc_jnkns.git"
    BRANCH_NAME    = "main"
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
          echo [CHECK] DVC repo var mi?
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

    stage('Configure DVC Remote') {
      steps {
        bat """
          call "%VENV%\\Scripts\\activate"
          echo [REMOTE] ensure default remote=storage -> %DVC_REMOTE%
          dvc remote add -d storage "%DVC_REMOTE%" 2>nul || dvc remote modify storage url "%DVC_REMOTE%"
          dvc remote list
        """
      }
    }

    stage('Track data if exists') {
      steps {
        bat """
          call "%VENV%\\Scripts\\activate"
          if exist "data\\student_scores.csv" (
            echo [DVC] add data\\student_scores.csv
            dvc add "data\\student_scores.csv" || echo already tracked
            git config user.name "%GIT_USER_NAME%"
            git config user.email "%GIT_USER_EMAIL%"
            git add "data\\student_scores.csv.dvc" .gitignore
            git commit -m "CI: track student_scores.csv via DVC" || echo no changes
          ) else (
            echo [INFO] data\\student_scores.csv yok, dvc add atlandi.
          )
        """
      }
    }

    stage('Ensure dvc.yaml (auto-create if missing)') {
      steps {
        bat """
          call "%VENV%\\Scripts\\activate"
          if not exist "dvc.yaml" (
            echo [INIT] dvc.yaml olusturuluyor (train stage)...
            if not exist models mkdir models
            dvc add "data\\student_scores.csv" 2>nul || echo already tracked
            dvc stage add -n train -d train.py -d data\\student_scores.csv -o models\\model.pkl python train.py -- --in data\\student_scores.csv --out models\\model.pkl
            git config user.name "%GIT_USER_NAME%"
            git config user.email "%GIT_USER_EMAIL%"
            git add dvc.yaml dvc.lock data\\student_scores.csv.dvc .gitignore
            git commit -m "CI: add dvc.yaml(train) if missing" || echo no changes
          ) else (
            echo [OK] dvc.yaml zaten var.
          )
        """
      }
    }

    stage('Train via DVC (repro)') {
      steps {
        bat """
          call "%VENV%\\Scripts\\activate"
          if exist "dvc.yaml" (
            echo [RUN] dvc repro -f
            dvc repro -f
          ) else (
            echo [SKIP] dvc.yaml yok, repro atlandi. & exit /b 0
          )
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
            git remote set-url origin https://%GIT_PAT%@github.com/furkanbuyuky/dvc_jnkns.git
            git push origin HEAD:%BRANCH_NAME%
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
