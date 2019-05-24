#!/usr/bin/env groovy

@Library('sec_ci_libs@v2-latest') _

def master_branches = ['master'] as String[]

task_wrapper('mesos-sec', master_branches, '8b793652-f26a-422f-a9ba-0d1e47eb9d89', '#dcos-security-ci') {

    pipeline {

    stage("Verify author") {
        user_is_authorized(master_branches, '8b793652-f26a-422f-a9ba-0d1e47eb9d89', '#dcos-security-ci')
    }

    stage('Checkout') {
        checkout scm
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
            sh "echo ${env.DOCKER_HUB_PASSWORD} | docker login -u '${env.DOCKER_HUB_USERNAME}' --password-stdin"
        }
        sh 'make docker-push'
    }

    stage("release") {
        when { tag "" }
        withCredentials([
            [
                $class: 'StringBinding',
                credentialsId: 'd146870f-03b0-4f6a-ab70-1d09757a51fc',
                variable: 'GITHUB_TOKEN',
            ]
        ]) {
            sh 'make release'
        }
    }

    }
}
