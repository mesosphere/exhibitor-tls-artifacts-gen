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
        sh 'make docker-push'
    }

    stage("release") {
        when { tag "" }
        sh "echo todo"
    }
}
