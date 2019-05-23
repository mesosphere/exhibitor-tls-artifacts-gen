#!/usr/bin/env groovy

@Library('sec_ci_libs@v2-latest') _

task_wrapper('mesos-sec', master_branches, '8b793652-f26a-422f-a9ba-0d1e47eb9d89', '#dcos-security-ci') {

    stage("Verify author") {
        user_is_authorized(master_branches, '8b793652-f26a-422f-a9ba-0d1e47eb9d89', '#dcos-security-ci')
    }

    stage("build") {
        sh 'make build'
    }

    stage("test") {
        sh 'make docker-test'
    }

    stage("publish docker") {
        withCredentials(
        [[$class: 'StringBinding',
            credentialsId: '7bdd2775-2911-41ba-918f-59c8ae52326d',
            variable: 'DOCKER_HUB_USERNAME'],
            [$class: 'StringBinding',
            credentialsId: '42f2e3fb-3f4f-47b2-a128-10ac6d0f6825',
            variable: 'DOCKER_HUB_PASSWORD'],
            [$class: 'StringBinding',
            credentialsId: '4551c307-10ae-40f9-a0ac-f1bb44206b5b',
            variable: 'DOCKER_HUB_EMAIL']
        ]) {
            sh "docker login -u '${env.DOCKER_HUB_USERNAME}' -p '${env.DOCKER_HUB_PASSWORD}'"
        }
        sh 'make docker-push'
    }

    stage("release") {
        when { tag "" }
        sh "echo todo"
    }
}
