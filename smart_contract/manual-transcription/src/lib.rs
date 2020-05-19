use borsh::{BorshDeserialize, BorshSerialize};
use near_sdk::{env, near_bindgen, Promise};
use std::collections::HashMap;
use std::collections::HashSet;

#[global_allocator]
static ALLOC: wee_alloc::WeeAlloc = wee_alloc::WeeAlloc::INIT;

#[near_bindgen]
#[derive(Default, BorshDeserialize, BorshSerialize)]
pub struct ManualTranscription {
    task_list: Vec<String>,
    pending_tasks: HashSet<String>,
    transcriptions: HashMap<String, (String, String)>,
    tips: HashMap<String, u128>,
    total_tipped: u128
}

#[near_bindgen]
impl ManualTranscription {
    pub fn req_transcription(&mut self, img: String) {
        self.task_list.push(img);
    }

    pub fn get_request(&self) -> Option<String> {
        let iterator = self.pending_tasks.iter();
        for x in iterator {
            return Some(x.clone());
        }
        return None;
    }

    pub fn move_request(&mut self) {
        let img_option = self.task_list.pop();
        if img_option.is_some() {
            let img = img_option.clone().unwrap();
            self.pending_tasks.insert(img.clone());
        }
    }

    pub fn submit_transcription(&mut self, img: String, trans: String) {
        let account_id = env::signer_account_id();
        self.transcriptions.insert(img.clone(), (trans, account_id));
        self.pending_tasks.remove(&img);
    }

    pub fn get_transcription(&self, img: String) -> Option<(String,String)> {
        let trans = self.transcriptions.get(&img);
        if trans.is_some() {
            return Some(trans.unwrap().clone());
        }
        return None;
    }

    pub fn rem_transcription(&mut self, img: String) {
        self.transcriptions.remove(&img);
    }

    #[payable]
    pub fn send_tip(&mut self, account_id: String) {
        let deposit = env::attached_deposit();
        let deposit_float = deposit as f64;

        self.total_tipped += deposit;

        let account_tips = self.tips.remove(&account_id);
        if account_tips.is_some() {
            let new_total = account_tips.unwrap() + deposit;
            self.tips.insert(account_id.clone(), new_total);
        } else {
            self.tips.insert(account_id.clone(), deposit);
        }

        let balance = env::account_balance() as f64;
        let max_bonus = 0.1 as f64;
        let tips_to_account = self.tips.get(&account_id.clone());
        let percent_tips;
        if tips_to_account.is_some() {
            let tips_float = tips_to_account.unwrap().clone() as f64;
            let tips_total_float = self.total_tipped as f64;
            percent_tips = tips_float/tips_total_float;
        } else {
            percent_tips = 0 as f64;
        }
        let amount = percent_tips.powf(2f64) * max_bonus * (balance - deposit_float) + 0.9 * deposit_float;
        let int_amount = amount as u128;
        Promise::new(account_id).transfer(int_amount);
    }
}

#[cfg(not(target_arch = "wasm32"))]
#[cfg(test)]
mod tests {
    use super::*;
    use near_sdk::MockedBlockchain;
    use near_sdk::{testing_env, VMContext};

    fn get_context(input: Vec<u8>, is_view: bool) -> VMContext {
        VMContext {
            current_account_id: "alice_near".to_string(),
            signer_account_id: "bob_near".to_string(),
            signer_account_pk: vec![0, 1, 2],
            predecessor_account_id: "carol_near".to_string(),
            input,
            block_index: 0,
            block_timestamp: 0,
            account_balance: 10,
            account_locked_balance: 0,
            storage_usage: 0,
            attached_deposit: 1,
            prepaid_gas: 10u64.pow(18),
            random_seed: vec![0, 1, 2],
            is_view,
            output_data_receivers: vec![],
            epoch_height: 0,
        }
    }

    #[test]
    fn req_get_sumbit_get_transcription() {
        let context = get_context(vec![], false);
        testing_env!(context);
        let mut contract = ManualTranscription::default();
        let img = "2dauPOVOLENlIyYqTGFftF3fqns+smh09mRpTpMLJXo=".to_string();
        contract.req_transcription(img.clone());
        contract.move_request();
        assert_eq!(
            img,
            contract.get_request().unwrap()
        );
        let trans = "test transcription".to_string();
        contract.submit_transcription(img.clone(),trans.clone());
        assert_eq!(
            (trans, "bob_near".to_string()),
            contract.get_transcription(img.clone()).unwrap()
        );
        contract.rem_transcription(img.clone());
    }

    #[test]
    fn send_tip() {
        let context = get_context(vec![], false);
        testing_env!(context);
        let mut contract = ManualTranscription::default();
        contract.send_tip("bob_near".to_string());
    }
}
