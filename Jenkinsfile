pipeline {
  agent any
  environment {
    VENV = ".venv"
    DVC_REMOTE = "C:\\dvc_storage"
    GIT_USER_NAME  = "jenkins-bot"
    GIT_USER_EMAIL = "jenkins@example.com"
  }
  stages {
    stage('Checkout') { steps { checkout scm } }

    stage('Setup Python & DVC') {
      steps {
        bat """
          python -m venv %VENV%
          call %VENV%\\Scripts\\activate
          pip install --upgrade pip
          pip install dvc
          dvc --version
        """
      }
    }

    stage('Sanity: DVC repo?') {
      steps {
        bat """
          echo WORKSPACE: %CD%
          dir /a
          if not exist .dvc (
            echo [WARN] .dvc klasoru yok! DVC init yapiliyor...
            call %VENV%\\Scripts\\activate
            dvc init
            git config user.name "%GIT_USER_NAME%"
            git config user.email "%GIT_USER_EMAIL%"
            git add .dvc .gitignore
            git commit -m "CI: init DVC (missing on agent)" || echo no changes
          ) else (
            echo [OK] .dvc klasoru mevcut.
          )
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

    // ... burada dvc add / dvc repro stage'lerin gelecek ...

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
}
