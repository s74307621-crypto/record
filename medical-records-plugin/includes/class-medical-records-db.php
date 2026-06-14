<?php
if (!defined('ABSPATH')) {
    exit;
}

class Medical_Records_DB {
    
    public static function get_doctors() {
        global $wpdb;
        $table_name = $wpdb->prefix . 'bookly_staff';
        return $wpdb->get_results("SELECT id, full_name, email, phone, category_id FROM {$table_name} WHERE visibility = 'public' ORDER BY position ASC", ARRAY_A);
    }
    
    public static function get_patients() {
        global $wpdb;
        $table_name = $wpdb->prefix . 'bookly_customers';
        return $wpdb->get_results("SELECT id, full_name, first_name, last_name, phone, email, birthday FROM {$table_name} ORDER BY created_at DESC", ARRAY_A);
    }
    
    public static function get_clinics() {
        global $wpdb;
        $table_name = $wpdb->prefix . 'bookly_categories';
        return $wpdb->get_results("SELECT id, name FROM {$table_name} ORDER BY position ASC", ARRAY_A);
    }
    
    public static function get_clinics_with_visits() {
        global $wpdb;
        $table_name = $wpdb->prefix . 'bookly_categories';
        $visits_table = $wpdb->prefix . 'mr_visits';
        
        $sql = "SELECT DISTINCT c.id, c.name 
                FROM {$table_name} c 
                INNER JOIN {$visits_table} v ON c.id = v.clinic_id 
                ORDER BY c.position ASC";
        
        return $wpdb->get_results($sql, ARRAY_A);
    }
    
    public static function get_doctors_with_visits($clinic_id = null) {
        global $wpdb;
        $staff_table = $wpdb->prefix . 'bookly_staff';
        $visits_table = $wpdb->prefix . 'mr_visits';
        
        if ($clinic_id) {
            $sql = "SELECT DISTINCT s.id, s.full_name 
                    FROM {$staff_table} s 
                    INNER JOIN {$visits_table} v ON s.id = v.doctor_id 
                    WHERE v.clinic_id = %d
                    ORDER BY s.position ASC";
            return $wpdb->get_results($wpdb->prepare($sql, $clinic_id), ARRAY_A);
        } else {
            $sql = "SELECT DISTINCT s.id, s.full_name 
                    FROM {$staff_table} s 
                    INNER JOIN {$visits_table} v ON s.id = v.doctor_id 
                    ORDER BY s.position ASC";
            return $wpdb->get_results($sql, ARRAY_A);
        }
    }
    
    public static function create_medical_record($customer_id, $doctor_id, $blood_group = '', $special_diseases = '', $age = 0, $current_medications = '', $medical_files = '') {
        global $wpdb;
        $table_name = $wpdb->prefix . 'mr_medical_records';
        
        $data = array(
            'customer_id' => $customer_id,
            'doctor_id' => $doctor_id,
            'blood_group' => sanitize_text_field($blood_group),
            'special_diseases' => sanitize_textarea_field($special_diseases),
            'age' => intval($age),
            'current_medications' => sanitize_textarea_field($current_medications),
            'medical_files' => sanitize_textarea_field($medical_files)
        );
        
        $format = array('%d', '%d', '%s', '%s', '%d', '%s', '%s');
        
        if ($wpdb->insert($table_name, $data, $format)) {
            return $wpdb->insert_id;
        }
        
        return false;
    }
    
    public static function delete_medical_record($record_id) {
        global $wpdb;
        $table_name = $wpdb->prefix . 'mr_medical_records';
        
        return $wpdb->delete($table_name, array('id' => $record_id), array('%d'));
    }
    
    public static function get_medical_record($record_id) {
        global $wpdb;
        $table_name = $wpdb->prefix . 'mr_medical_records';
        
        return $wpdb->get_row($wpdb->prepare("SELECT * FROM {$table_name} WHERE id = %d", $record_id), ARRAY_A);
    }
    
    public static function get_medical_record_by_customer($customer_id) {
        global $wpdb;
        $table_name = $wpdb->prefix . 'mr_medical_records';
        
        return $wpdb->get_row($wpdb->prepare("SELECT * FROM {$table_name} WHERE customer_id = %d", $customer_id), ARRAY_A);
    }
    
    public static function update_medical_record($record_id, $data) {
        global $wpdb;
        $table_name = $wpdb->prefix . 'mr_medical_records';
        
        $format = array();
        foreach ($data as $key => $value) {
            $format[] = is_numeric($value) ? '%d' : '%s';
        }
        
        return $wpdb->update($table_name, $data, array('id' => $record_id), $format, array('%d'));
    }
    
    public static function create_visit($medical_record_id, $doctor_id, $clinic_id, $complaint = '', $diagnosis = '', $medications = '', $files = '') {
        global $wpdb;
        $table_name = $wpdb->prefix . 'mr_visits';
        
        $data = array(
            'medical_record_id' => $medical_record_id,
            'doctor_id' => $doctor_id,
            'clinic_id' => $clinic_id,
            'complaint' => sanitize_textarea_field($complaint),
            'diagnosis' => sanitize_textarea_field($diagnosis),
            'medications' => sanitize_textarea_field($medications),
            'files' => sanitize_textarea_field($files)
        );
        
        $format = array('%d', '%d', '%d', '%s', '%s', '%s', '%s');
        
        if ($wpdb->insert($table_name, $data, $format)) {
            return $wpdb->insert_id;
        }
        
        return false;
    }
    
    public static function get_visits($medical_record_id, $filters = array()) {
        global $wpdb;
        $table_name = $wpdb->prefix . 'mr_visits';
        $staff_table = $wpdb->prefix . 'bookly_staff';
        $clinics_table = $wpdb->prefix . 'bookly_categories';
        
        $where = array("v.medical_record_id = %d");
        $params = array($medical_record_id);
        
        if (!empty($filters['doctor_id'])) {
            $where[] = "v.doctor_id = %d";
            $params[] = $filters['doctor_id'];
        }
        
        if (!empty($filters['clinic_id'])) {
            $where[] = "v.clinic_id = %d";
            $params[] = $filters['clinic_id'];
        }
        
        if (!empty($filters['date_from'])) {
            $where[] = "DATE(v.visit_date) >= %s";
            $params[] = $filters['date_from'];
        }
        
        if (!empty($filters['date_to'])) {
            $where[] = "DATE(v.visit_date) <= %s";
            $params[] = $filters['date_to'];
        }
        
        $where_clause = implode(' AND ', $where);
        
        $sql = "SELECT v.*, s.full_name as doctor_name, c.name as clinic_name 
                FROM {$table_name} v 
                LEFT JOIN {$staff_table} s ON v.doctor_id = s.id 
                LEFT JOIN {$clinics_table} c ON v.clinic_id = c.id 
                WHERE {$where_clause} 
                ORDER BY v.visit_date DESC";
        
        return $wpdb->get_results($wpdb->prepare($sql, $params), ARRAY_A);
    }
    
    public static function get_visit_details($visit_id) {
        global $wpdb;
        $table_name = $wpdb->prefix . 'mr_visits';
        $staff_table = $wpdb->prefix . 'bookly_staff';
        $clinics_table = $wpdb->prefix . 'bookly_categories';
        
        $sql = "SELECT v.*, s.full_name as doctor_name, c.name as clinic_name 
                FROM {$table_name} v 
                LEFT JOIN {$staff_table} s ON v.doctor_id = s.id 
                LEFT JOIN {$clinics_table} c ON v.clinic_id = c.id 
                WHERE v.id = %d";
        
        return $wpdb->get_row($wpdb->prepare($sql, $visit_id), ARRAY_A);
    }
    
    public static function patient_exists_in_bookly($customer_id) {
        global $wpdb;
        $table_name = $wpdb->prefix . 'bookly_customers';
        
        $result = $wpdb->get_var($wpdb->prepare("SELECT COUNT(*) FROM {$table_name} WHERE id = %d", $customer_id));
        
        return $result > 0;
    }
    
    public static function doctor_exists_in_bookly($doctor_id) {
        global $wpdb;
        $table_name = $wpdb->prefix . 'bookly_staff';
        
        $result = $wpdb->get_var($wpdb->prepare("SELECT COUNT(*) FROM {$table_name} WHERE id = %d", $doctor_id));
        
        return $result > 0;
    }
}
