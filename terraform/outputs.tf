output "worker_public_ip" {
  description = "Public IP of the Worker instance"
  value       = aws_instance.worker_instance.public_ip
}

output "questdb_public_ip" {
  description = "Public IP of the QuestDB instance"
  value       = aws_instance.questdb_instance.public_ip
}
