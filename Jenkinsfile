pipeline {
  agent any

  environment {
    VENV = ".venv"
    DVC_REMOTE = "C:\\dvc_storage"   // Jenkins agent'ta erişilebilen bir yol olmalı
    GIT_USER_NAME  = "jenkins-bot"
    GIT_USER_EMAIL = "jenkins@example.com"
  }

  stages {
    stage('Checkout') {
      steps { checkout scm }
    }

    stage('Setup Python & DVC') {
      steps {
        bat """
          python -m venv %VENV%
          call %VENV%\\Scripts\\activate
          pip install --upgrade pip
          pip install dvc
          REM Model için tipik paketler (gerekiyorsa ekle/sil)
          pip install pandas scikit-learn joblib
          dvc --version
        """
      }
    }

    stage('Configure DVC Remote') {
      steps {
        bat """
          call %VENV%\\Scripts\\activate
          dvc remote add -d storage "%DVC_REMOTE%" || dvc remote modify storage url "%DVC_REMOTE%"
        """
      }
    }

    stage('Train via DVC (repro)') {
      steps {
        bat """
          call %VENV%\\Scripts\\activate
          dvc repro -f
        """
      }
    }

    stage('Commit Metadata (if changed)') {
      steps {
        bat """
          call %VENV%\\Scripts\\activate
          git config user.name "%GIT_USER_NAME%"
          git config user.email "%GIT_USER_EMAIL%"
          git add dvc.yaml dvc.lock .gitignore
          git commit -m "CI: update DVC pipeline lock" || echo no changes
        """
      }
    }

    stage('Push Data & Code') {
      steps {
        withCredentials([string(credentialsId: 'git-pat', variable: 'GIT_PAT')]) {
          bat """
            call %VENV%\\Scripts\\activate
            dvc push
            git remote set-url origin https://%GIT_PAT%@github.com/furkanbuyuky/dvc_jnkns.git
            git push origin HEAD:main
          """
        }
      }
    }
  }

  post {
    always {
      bat 'rmdir /S /Q .venv 2>nul || echo venv cleanup skipped'
    }
  }
}
