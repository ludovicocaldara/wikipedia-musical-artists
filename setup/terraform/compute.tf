resource "tls_private_key" "provisioner_keypair" {
  algorithm   = "RSA"
  rsa_bits = "4096"
}

resource "oci_core_instance" "compute" {
  availability_domain = data.oci_identity_availability_domains.availability_domains.availability_domains[0].name
  compartment_id      = var.compartment_ocid
  shape               = var.vm_shape
  display_name        = var.lab_name

  source_details {
    source_id               = data.oci_core_images.vm_images.images[0].id
    source_type             = "image"
    boot_volume_size_in_gbs = var.boot_volume_size_in_gbs
  }

  create_vnic_details {
    assign_public_ip        = true
    subnet_id               = oci_core_subnet.db_subnet.id
    display_name            = "${var.lab_name}-vnic"
    hostname_label          = "host-${var.lab_name}"
  }

  metadata = {
    ssh_authorized_keys = "${tls_private_key.provisioner_keypair.public_key_openssh}"
  }

}

