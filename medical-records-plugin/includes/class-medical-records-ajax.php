<?php
if (!defined('ABSPATH')) {
    exit;
}

class Medical_Records_Ajax {
    
    public static function ajax_create_medical_record() {
        try {
            check_ajax_referer('mr_frontend_nonce', 'nonce');
            
            // Allow both admin and users with edit_posts capability (doctors)
            if (!current_user_can('edit_posts') && !current_user_can('manage_options')) {
                $current_user = wp_get_current_user();
                global $wpdb;
                $staff_table = $wpdb->prefix . 'bookly_staff';
                $is_staff = $wpdb->get_var($wpdb->prepare(
                    "SELECT COUNT(*) FROM {$staff_table} WHERE wp_user_id = %d",
                    $current_user->ID
                ));
                
                if ($is_staff == 0) {
                    wp_send_json_error(array('message' => __('دسترسی غیرمجاز', 'medical-records')), 403);
                }
            }
            
            $customer_id = intval($_POST['customer_id']);
            $doctor_id = intval($_POST['doctor_id']);
            $blood_group = sanitize_text_field($_POST['blood_group']);
            $special_diseases = sanitize_textarea_field($_POST['special_diseases']);
            $age = intval($_POST['age']);
            $current_medications = sanitize_textarea_field($_POST['current_medications']);
            $medical_files = sanitize_textarea_field($_POST['medical_files']);
            
            if (empty($customer_id) || empty($doctor_id)) {
                wp_send_json_error(array('message' => __('اطلاعات ناقص است', 'medical-records')), 400);
            }
            
            if (!Medical_Records_DB::patient_exists_in_bookly($customer_id)) {
                wp_send_json_error(array('message' => __('بیمار در سیستم یافت نشد', 'medical-records')), 404);
            }
            
            if (!Medical_Records_DB::doctor_exists_in_bookly($doctor_id)) {
                wp_send_json_error(array('message' => __('پزشک در سیستم یافت نشد', 'medical-records')), 404);
            }
            
            $record_id = Medical_Records_DB::create_medical_record(
                $customer_id,
                $doctor_id,
                $blood_group,
                $special_diseases,
                $age,
                $current_medications,
                $medical_files
            );
            
            if ($record_id) {
                wp_send_json_success(array(
                    'message' => __('پرونده با موفقیت ایجاد شد', 'medical-records'),
                    'record_id' => $record_id
                ));
            } else {
                wp_send_json_error(array('message' => __('خطا در ایجاد پرونده', 'medical-records')), 500);
            }
            
        } catch (Exception $e) {
            error_log('MR Error - create_medical_record: ' . $e->getMessage());
            wp_send_json_error(array('message' => __('خطای سرور', 'medical-records')), 500);
        }
    }
    
    public static function ajax_delete_medical_record() {
        try {
            check_ajax_referer('mr_admin_nonce', 'nonce');
            
            if (!current_user_can('manage_options')) {
                wp_send_json_error(array('message' => __('دسترسی غیرمجاز', 'medical-records')), 403);
            }
            
            $record_id = intval($_POST['record_id']);
            
            if (empty($record_id)) {
                wp_send_json_error(array('message' => __('شناسه پرونده نامعتبر است', 'medical-records')), 400);
            }
            
            $result = Medical_Records_DB::delete_medical_record($record_id);
            
            if ($result) {
                wp_send_json_success(array('message' => __('پرونده با موفقیت حذف شد', 'medical-records')));
            } else {
                wp_send_json_error(array('message' => __('خطا در حذف پرونده', 'medical-records')), 500);
            }
            
        } catch (Exception $e) {
            error_log('MR Error - delete_medical_record: ' . $e->getMessage());
            wp_send_json_error(array('message' => __('خطای سرور', 'medical-records')), 500);
        }
    }
    
    public static function ajax_get_medical_record() {
        try {
            check_ajax_referer('mr_frontend_nonce', 'nonce');
            
            // Allow both admin and users with edit_posts capability (doctors)
            if (!current_user_can('edit_posts') && !current_user_can('manage_options')) {
                $current_user = wp_get_current_user();
                global $wpdb;
                $staff_table = $wpdb->prefix . 'bookly_staff';
                $is_staff = $wpdb->get_var($wpdb->prepare(
                    "SELECT COUNT(*) FROM {$staff_table} WHERE wp_user_id = %d",
                    $current_user->ID
                ));
                
                if ($is_staff == 0) {
                    wp_send_json_error(array('message' => __('دسترسی غیرمجاز', 'medical-records')), 403);
                }
            }
            
            $record_id = intval($_GET['record_id']);
            
            if (empty($record_id)) {
                wp_send_json_error(array('message' => __('شناسه پرونده نامعتبر است', 'medical-records')), 400);
            }
            
            $record = Medical_Records_DB::get_medical_record($record_id);
            
            if ($record) {
                wp_send_json_success(array('record' => $record));
            } else {
                wp_send_json_error(array('message' => __('پرونده یافت نشد', 'medical-records')), 404);
            }
            
        } catch (Exception $e) {
            error_log('MR Error - get_medical_record: ' . $e->getMessage());
            wp_send_json_error(array('message' => __('خطای سرور', 'medical-records')), 500);
        }
    }
    
    public static function ajax_create_visit() {
        try {
            check_ajax_referer('mr_frontend_nonce', 'nonce');
            
            // Allow both admin and users with edit_posts capability (doctors)
            if (!current_user_can('edit_posts') && !current_user_can('manage_options')) {
                $current_user = wp_get_current_user();
                global $wpdb;
                $staff_table = $wpdb->prefix . 'bookly_staff';
                $is_staff = $wpdb->get_var($wpdb->prepare(
                    "SELECT COUNT(*) FROM {$staff_table} WHERE wp_user_id = %d",
                    $current_user->ID
                ));
                
                if ($is_staff == 0) {
                    wp_send_json_error(array('message' => __('دسترسی غیرمجاز', 'medical-records')), 403);
                }
            }
            
            $medical_record_id = intval($_POST['medical_record_id']);
            $doctor_id = intval($_POST['doctor_id']);
            $clinic_id = intval($_POST['clinic_id']);
            $complaint = sanitize_textarea_field($_POST['complaint']);
            $diagnosis = sanitize_textarea_field($_POST['diagnosis']);
            $medications = sanitize_textarea_field($_POST['medications']);
            $files = sanitize_textarea_field($_POST['files']);
            
            if (empty($medical_record_id) || empty($doctor_id) || empty($clinic_id)) {
                wp_send_json_error(array('message' => __('اطلاعات ناقص است', 'medical-records')), 400);
            }
            
            $visit_id = Medical_Records_DB::create_visit(
                $medical_record_id,
                $doctor_id,
                $clinic_id,
                $complaint,
                $diagnosis,
                $medications,
                $files
            );
            
            if ($visit_id) {
                wp_send_json_success(array(
                    'message' => __('ویزیت با موفقیت ثبت شد', 'medical-records'),
                    'visit_id' => $visit_id
                ));
            } else {
                wp_send_json_error(array('message' => __('خطا در ثبت ویزیت', 'medical-records')), 500);
            }
            
        } catch (Exception $e) {
            error_log('MR Error - create_visit: ' . $e->getMessage());
            wp_send_json_error(array('message' => __('خطای سرور', 'medical-records')), 500);
        }
    }
    
    public static function ajax_get_visits() {
        try {
            check_ajax_referer('mr_frontend_nonce', 'nonce');
            
            // Allow both admin and users with edit_posts capability (doctors)
            if (!current_user_can('edit_posts') && !current_user_can('manage_options')) {
                $current_user = wp_get_current_user();
                global $wpdb;
                $staff_table = $wpdb->prefix . 'bookly_staff';
                $is_staff = $wpdb->get_var($wpdb->prepare(
                    "SELECT COUNT(*) FROM {$staff_table} WHERE wp_user_id = %d",
                    $current_user->ID
                ));
                
                if ($is_staff == 0) {
                    wp_send_json_error(array('message' => __('دسترسی غیرمجاز', 'medical-records')), 403);
                }
            }
            
            $medical_record_id = intval($_GET['medical_record_id']);
            $filters = array();
            
            if (!empty($_GET['doctor_id'])) {
                $filters['doctor_id'] = intval($_GET['doctor_id']);
            }
            
            if (!empty($_GET['clinic_id'])) {
                $filters['clinic_id'] = intval($_GET['clinic_id']);
            }
            
            if (!empty($_GET['date_from'])) {
                $filters['date_from'] = sanitize_text_field($_GET['date_from']);
            }
            
            if (!empty($_GET['date_to'])) {
                $filters['date_to'] = sanitize_text_field($_GET['date_to']);
            }
            
            if (empty($medical_record_id)) {
                wp_send_json_error(array('message' => __('شناسه پرونده نامعتبر است', 'medical-records')), 400);
            }
            
            $visits = Medical_Records_DB::get_visits($medical_record_id, $filters);
            
            wp_send_json_success(array('visits' => $visits));
            
        } catch (Exception $e) {
            error_log('MR Error - get_visits: ' . $e->getMessage());
            wp_send_json_error(array('message' => __('خطای سرور', 'medical-records')), 500);
        }
    }
    
    public static function ajax_get_visit_details() {
        try {
            check_ajax_referer('mr_frontend_nonce', 'nonce');
            
            // Allow both admin and users with edit_posts capability (doctors)
            if (!current_user_can('edit_posts') && !current_user_can('manage_options')) {
                $current_user = wp_get_current_user();
                global $wpdb;
                $staff_table = $wpdb->prefix . 'bookly_staff';
                $is_staff = $wpdb->get_var($wpdb->prepare(
                    "SELECT COUNT(*) FROM {$staff_table} WHERE wp_user_id = %d",
                    $current_user->ID
                ));
                
                if ($is_staff == 0) {
                    wp_send_json_error(array('message' => __('دسترسی غیرمجاز', 'medical-records')), 403);
                }
            }
            
            $visit_id = intval($_GET['visit_id']);
            
            if (empty($visit_id)) {
                wp_send_json_error(array('message' => __('شناسه ویزیت نامعتبر است', 'medical-records')), 400);
            }
            
            $visit = Medical_Records_DB::get_visit_details($visit_id);
            
            if ($visit) {
                wp_send_json_success(array('visit' => $visit));
            } else {
                wp_send_json_error(array('message' => __('ویزیت یافت نشد', 'medical-records')), 404);
            }
            
        } catch (Exception $e) {
            error_log('MR Error - get_visit_details: ' . $e->getMessage());
            wp_send_json_error(array('message' => __('خطای سرور', 'medical-records')), 500);
        }
    }
    
    public static function ajax_save_medical_history() {
        try {
            check_ajax_referer('mr_frontend_nonce', 'nonce');
            
            $customer_id = intval($_POST['customer_id']);
            $blood_group = sanitize_text_field($_POST['blood_group']);
            $special_diseases = sanitize_textarea_field($_POST['special_diseases']);
            $age = intval($_POST['age']);
            $current_medications = sanitize_textarea_field($_POST['current_medications']);
            $medical_files = sanitize_textarea_field($_POST['medical_files']);
            
            if (empty($customer_id)) {
                wp_send_json_error(array('message' => __('شناسه بیمار نامعتبر است', 'medical-records')), 400);
            }
            
            $existing_record = Medical_Records_DB::get_medical_record_by_customer($customer_id);
            
            if ($existing_record) {
                // Update existing record
                $data = array(
                    'blood_group' => $blood_group,
                    'special_diseases' => $special_diseases,
                    'age' => $age,
                    'current_medications' => $current_medications,
                    'medical_files' => $medical_files
                );
                
                $result = Medical_Records_DB::update_medical_record($existing_record['id'], $data);
                
                if ($result !== false) {
                    wp_send_json_success(array('message' => __('سوابق پزشکی با موفقیت ثبت شد', 'medical-records')));
                } else {
                    wp_send_json_error(array('message' => __('خطا در ثبت سوابق', 'medical-records')), 500);
                }
            } else {
                // Create new record for patient (self-registration)
                global $wpdb;
                $staff_table = $wpdb->prefix . 'bookly_staff';
                $current_user = wp_get_current_user();
                
                // Find first available doctor or use customer's associated doctor
                $default_doctor_id = $wpdb->get_var("SELECT id FROM {$staff_table} LIMIT 1");
                
                if (!$default_doctor_id) {
                    wp_send_json_error(array('message' => __('پزشکی یافت نشد', 'medical-records')), 404);
                }
                
                $record_id = Medical_Records_DB::create_medical_record(
                    $customer_id,
                    intval($default_doctor_id),
                    $blood_group,
                    $special_diseases,
                    $age,
                    $current_medications,
                    $medical_files
                );
                
                if ($record_id) {
                    wp_send_json_success(array(
                        'message' => __('پرونده با موفقیت ایجاد شد', 'medical-records'),
                        'record_id' => $record_id
                    ));
                } else {
                    wp_send_json_error(array('message' => __('خطا در ایجاد پرونده', 'medical-records')), 500);
                }
            }
            
        } catch (Exception $e) {
            error_log('MR Error - save_medical_history: ' . $e->getMessage());
            wp_send_json_error(array('message' => __('خطای سرور', 'medical-records')), 500);
        }
    }
    
    public static function ajax_upload_file() {
        try {
            if (!isset($_FILES['file'])) {
                wp_send_json_error(array('message' => __('فایلی ارسال نشده است', 'medical-records')), 400);
            }
            
            $file = $_FILES['file'];
            
            $allowed_types = array('image/jpeg', 'image/png', 'image/gif', 'application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document');
            
            if (!in_array($file['type'], $allowed_types)) {
                wp_send_json_error(array('message' => __('نوع فایل مجاز نیست', 'medical-records')), 400);
            }
            
            $upload_dir = wp_upload_dir();
            $mr_dir = $upload_dir['basedir'] . '/medical-records/';
            
            if (!file_exists($mr_dir)) {
                wp_mkdir_p($mr_dir);
            }
            
            $filename = time() . '_' . sanitize_file_name($file['name']);
            $file_path = $mr_dir . $filename;
            
            if (move_uploaded_file($file['tmp_name'], $file_path)) {
                $file_url = $upload_dir['baseurl'] . '/medical-records/' . $filename;
                wp_send_json_success(array(
                    'file_url' => $file_url,
                    'file_name' => $filename
                ));
            } else {
                wp_send_json_error(array('message' => __('خطا در آپلود فایل', 'medical-records')), 500);
            }
            
        } catch (Exception $e) {
            error_log('MR Error - upload_file: ' . $e->getMessage());
            wp_send_json_error(array('message' => __('خطای سرور', 'medical-records')), 500);
        }
    }
    
    public static function ajax_search_patients() {
        try {
            check_ajax_referer('mr_frontend_nonce', 'nonce');
            
            // Allow both admin and users with edit_posts capability (doctors)
            if (!current_user_can('edit_posts') && !current_user_can('manage_options')) {
                // Check if user is a Bookly staff member
                $current_user = wp_get_current_user();
                global $wpdb;
                $staff_table = $wpdb->prefix . 'bookly_staff';
                $is_staff = $wpdb->get_var($wpdb->prepare(
                    "SELECT COUNT(*) FROM {$staff_table} WHERE wp_user_id = %d",
                    $current_user->ID
                ));
                
                if ($is_staff == 0) {
                    wp_send_json_error(array('message' => __('دسترسی غیرمجاز', 'medical-records')), 403);
                }
            }
            
            $term = isset($_GET['term']) ? sanitize_text_field($_GET['term']) : '';
            
            global $wpdb;
            $table_name = $wpdb->prefix . 'bookly_customers';
            
            $sql = "SELECT id, full_name FROM {$table_name} WHERE full_name LIKE %s ORDER BY full_name ASC LIMIT 20";
            $results = $wpdb->get_results($wpdb->prepare($sql, '%' . $wpdb->esc_like($term) . '%'), ARRAY_A);
            
            $response = array();
            foreach ($results as $patient) {
                $response[] = array(
                    'id' => $patient['id'],
                    'text' => $patient['full_name']
                );
            }
            
            wp_send_json_success(array('results' => $response));
            
        } catch (Exception $e) {
            error_log('MR Error - search_patients: ' . $e->getMessage());
            wp_send_json_error(array('message' => __('خطای سرور', 'medical-records')), 500);
        }
    }
}

add_action('wp_ajax_mr_create_medical_record', array('Medical_Records_Ajax', 'ajax_create_medical_record'));
add_action('wp_ajax_mr_delete_medical_record', array('Medical_Records_Ajax', 'ajax_delete_medical_record'));
add_action('wp_ajax_mr_get_medical_record', array('Medical_Records_Ajax', 'ajax_get_medical_record'));
add_action('wp_ajax_mr_create_visit', array('Medical_Records_Ajax', 'ajax_create_visit'));
add_action('wp_ajax_mr_get_visits', array('Medical_Records_Ajax', 'ajax_get_visits'));
add_action('wp_ajax_mr_get_visit_details', array('Medical_Records_Ajax', 'ajax_get_visit_details'));
add_action('wp_ajax_mr_save_medical_history', array('Medical_Records_Ajax', 'ajax_save_medical_history'));
add_action('wp_ajax_mr_upload_file', array('Medical_Records_Ajax', 'ajax_upload_file'));
add_action('wp_ajax_nopriv_mr_upload_file', array('Medical_Records_Ajax', 'ajax_upload_file'));
add_action('wp_ajax_mr_search_patients', array('Medical_Records_Ajax', 'ajax_search_patients'));
